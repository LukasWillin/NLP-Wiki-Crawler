# coding=utf-8
#
# Original Source (24 September 2011) http://www.netinstructions.com/how-to-make-a-web-crawler-in-under-50-lines-of-python-code/
# Original Author: Stephen
# License: -
#
# Adapted for nlp 4iCa @FHNW Fachhochschule Nordwestschweiz
# Author: Lukas Willin
# Date: 14.15.2019
# License: GPLv3

from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen
from urllib import parse
from urllib import error
from contextlib2 import closing
from math import ceil
import random
import pandas
import shutil
import pickle
import sys
import time
import re
import os

# Ressources used for multiprocessing:
# - (About threads but principles apply) https://www.codementor.io/lance/simple-parallelism-in-python-du107klle
# - (About threads but principles apply) https://www.metachris.com/2016/04/python-threadpool/
# - https://www.blog.pythonlibrary.org/2016/08/02/python-201-a-multiprocessing-tutorial/
# - https://pymotw.com/2/multiprocessing/basics.html
# - https://pythontic.com/multiprocessing/process/start
# - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.get_context

from multiprocessing import Queue, JoinableQueue
from multiprocessing import Pool
from multiprocessing import Process, Lock

# Signal trapping
import signal
import sys

class Excl:

    exclusions = set([])
    re_excl_split = re.compile(r'[\t\n\r\ ]')
    re_exclude_words = None
    excl_string = ''
    
    def add_to_exclusion_list(from_string):
        parts = Excl.re_excl_split.split(from_string)
        for p in parts:
            if (len(p) > 0):
                Excl.exclusions.add(r'(\b' + p + r'\b)|')
        Excl.excl_string = r'('
        for e in Excl.exclusions:
            Excl.excl_string += e
        Excl.excl_string = Excl.excl_string[:-1]
        Excl.excl_string += r')'
        Excl.re_exclude_words = re.compile(Excl.excl_string)

    re_space = re.compile(r'[\t\n\r\.\:\;\,\-\_\"\?\!\(\)\{\}\*\@\+\-\<\>\/\\\|0-9]+', flags=re.MULTILINE)
    re_rem = re.compile(r'[^a-zA-ZäÄöÖüÜëËïÏåÅáÁàÀąĄóÓòÒøØèÈéÉêÊęĘċĊćĆčČùâúÚùÙÂôÔĩĨìÌíÍńŃǹǸñÑłŁƚȽżŻšŠśŚß\ ]|[\']')
    re_excl_rule = re.compile(r'[a-zäöüëïåáàąóòøèéêęċćčùâúùôĩìíńǹñłƚżšśß]{0,1}([A-ZÄÖÜËÏÅÁÀĄÓÒØÈÉÊĘĊĆČÚÙÂÔĨÌÍŃǸÑŁȽŻŠŚ][a-zäöüëïåáàąóòøèéêęċćčùâúùôĩìíńǹñłƚżšśß]*){2,}(?![\;\-\/\:\%\.\_\)])\b')  # Remove words that do have Big Letters inbetween
    re_rem_space = re.compile(r'\ {2,}')

    def stripHtml(html):
        html = Excl.re_space.sub(' ', html)
        html = Excl.re_rem.sub('', html)
        html = Excl.re_exclude_words.sub(' ', html)
        return Excl.re_excl_rule.sub(' ', html)

    def clean(text):
        return Excl.re_rem_space.sub(' ', text)

Excl.add_to_exclusion_list(r'autocollapse statecollapsed wikipedia Wikipedia wpsearch QUERY TERMS ShortSearch document documentElement className most interwikis Page document documentElement className replace      s client nojs  s       client js        titlePunishmentoldid window RLQwindow RLQ    push function   mw config set   wgCanonicalNamespace      wgCanonicalSpecialPageName  false  wgNamespaceNumber     wgPageName   P value   wgTitle   P value   wgCurRevisionId             wgRevisionId             wgArticleId          wgIsArticle  true  wgIsRedirect  false  wgAction   view   wgUserName  null  wgUserGroups       wgCategories ')
Excl.add_to_exclusion_list(r'editWarning wgStructuredChangeFilters Expand Gadget usage statistics Graph sandbox List wikis system sandbox Try hieroglyph markup View interwiki Wiki sets Redirecting special mediawiki action edit collapsibleFooter href  site   mediawiki page startup   mediawiki page ready   mediawiki searchSuggest    charinsert    gadget teahouse gadget ReferenceTooltips gadget watchlist notice gadget DRN wizard gadget charinsert gadget refToolbar gadget extra toolbar buttons gadget switcher centralauth centralautologin CodeMirror   mmv head   mmv bootstrap autostart popups visualEditor desktopArticleTarget init visualEditor targetLoader    eventLogging wikimediaEvents navigationTiming    uls compactlinks    uls interface    quicksurveys init    centralNotice geoIP   skins vector js  mw loader load RLPAGEMODULES')
Excl.add_to_exclusion_list(r'mw config set wgInternalRedirectTargetUrl herit inherit inherit inherit cs hidden error cs visible error cs maint aa cs subscription cs registration cs format cs kern cs kern wl cs kern cs kern wl pageneeded wgCanonicalNamespace wgRedirectedFrom Sitenotice title Hjlp sitenotice UTC  wgCanonicalSpecialPageName  false  wgNamespaceNumber    ext wgPageName   P value   wgTitle   P value   wgCurRevisionId Wikimedia Commons Wikidata index php Creative Commons Attribution ShareAlike License         wgRevisionId             wgArticleId          wgIsArticle  true  wgIsRedirect  false  wgAction   view   wgUserName  null  wgUserGroups td tr tbody table      wgCategories   Articles with short description')
Excl.add_to_exclusion_list(r'wgRelevantPageName wgBackendResponseTime wgHostname wgRelevantArticleId wgSiteNoticeId w titleWikipedia Log Namespaces dismissableSiteNotice cqd ng required helpers helplink htmlform ooui htmlform DateInputWidget userSuggest htmlform htmlform ooui UserInputWidget DateInputWidget thanks corethank   wgRequestId wgCSPNonce  wgIsProbablyEditable  wgRelevantPageIsProbablyEditable  wgRestrictionEdit  wgRestrictionMove  wgMediaViewerOnClick  wgMediaViewerEnabledByDefault  wgPopupsReferencePreviews  wgPopupsConflictsWithNavPopupGadget  wgVisualEditor  pageLanguageCode  en  pageLanguageDir  ltr  pageVariantFallbacks  en  wgMFDisplayWikibaseDescriptions  search  nearby    tagline   wgRelatedArticles  wgRelatedArticlesUseCirrusSearch  wgRelatedArticlesOnlyUseCirrusSearch  wgWMESchemaEditAttemptStepOversample  wgPoweredByHHVM  wgULSCurrentAutonym  English  wgNoticeProject   wgCentralNoticeCookiesToDelete  wgCentralNoticeCategoriesUsingLegacy  Fundraising  fundraising  wgWikibaseItemId  Q     wgCentralAuthMobileDomain  wgEditSubmitButtonLabelPublish    state   styles    globalCssJs user styles    globalCssJs styles    styles   noscript   user styles    globalCssJs user    globalCssJs    user   user options   user tokens  loading  cite styles    math styles    legacy shared    legacy commonPrint    toc styles   wikibase      noscript    interlanguage    wikimediaBadges    d styles    skinning     styles     implement user tokens tffind  jQuery require module  displaystyle X displaystyle  alpha Leftrightarrow wgPageParseReport limitreport cputime  walltime  ppvisitednodes  limit  ppgeneratednodes  limit  postexpandincludesize  limit  templateargumentsize limit  expansiondepth  limit  expensivefunctioncount  limit unstrip depth  limit  unstrip size  limit  entityaccesscount  limit timingprofile   Templat References    total   Templat Cite journal   Templat Main other scribunto limitreport timeusage   limit   limitreport memusage   limit  cachereport origin timestamp  ttl  transientcontent      context  https  schema  type  Article  name  Nilai url  https  wiki Nilai sameAs  http  www wikidata  entity  mainEntity  nomin  user tokens  editToken     patrolToken     watchToken     csrfToken        cite ux enhancements  math scripts         toc')
Excl.add_to_exclusion_list(r'parser output RLSTATE plainlist ul list main wgIsMainPage tmulti thumbinner display flex flex direction column autoconfirmed sysop wgCoordinates parser output tmulti trow display flex flex direction row clear left flex wrap wrap width  box sizing border box  parser output tmulti tsingle margin px float left  parser output tmulti theader clear both font weight bold text align center align self center background color transparent width  parser output tmulti thumbcaption text align left background color transparent  parser output tmulti text align left text align left  parser output tmulti text align right text align right  parser output tmulti text align center text align center all and max width px parser output tmulti thumbinner width  important box sizing border box max width none important align items center  parser output tmulti trow justify content center  parser output tmulti tsingle float none important max width  important box sizing border box text align center  parser output tmulti thumbcaption text align center')
Excl.add_to_exclusion_list(r'wgBreakFrames wgMonthNamesShort iM AAACN LCCN identifiers articles VIAF identifiers articles WorldCat VIAF identifiers Book Compare export  wgFlaggedRevsParams tags accuracy levels  quality  pristine wgStableRevisionId    de  de     Deutsch                   flaggedRevs basic   wzrrbt   variant  de          editMenus  WikiMiniAtlas  OpenStreetMap  CommonsDirekt      categoryPage categoryTree tmh thumbnail xs k af categoryTree MediaWikiPlayer PopUpMediaTransform startUp flaggedRevs advanced classNamedocument  Collider Detector at Fermilab dO wAAAAK    wgFlaggedRevsParams tags accuracy levels  quality  pristine wgStableRevisionId    de  de     Deutsch Line data file data file td                    flaggedRevs basic   wzrrbt   variant  de            editMenus  WikiMiniAtlas  OpenStreetMap  CommonsDirekt      startUp flaggedRevs advanced var nodedocument getElementById  dismissablenotice anonplace  if node node outerHTML u  Cdiv class  dismissable u  E u  Cdiv class  dismissable close  u  E u  Ca tabindex role button  u  Ezarrar u  C a u  E u  C div u  E u  Cdiv class  dismissable body  u  E u  Cdiv id localNotice  lang ast  dir  u  E u  Ctable style  class noprint plainlinks ambox ambox u  E n u  Ctbody u  E u  Ctr u  E n u  Ctd class ambox image  u  E n u  Cdiv style  u  E u  Cimg alt  src upload wikimedia org commons thumb a ac Noun Project maintenance icon cc svg Noun Project maintenance icon cc svg png  decoding async height  srcset upload wikimedia org commons thumb a ac Noun Project maintenance icon cc svg Noun Project maintenance icon cc svg png x wgPageContentLanguage  de  wgPageContentModel  wikitext  wgSeparatorTransformTable  t t wgDigitTransformTable  wgDefaultDateFormat  dmy  wgMonthNames')
Excl.add_to_exclusion_list(r'templates January span dotted cursor cs ws c Wikisource logo Wikisource logo no repeat wgRelevantUserName bibcoded see bibcode Bibcode February March April May June July August September October November December Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Template User Talk Pages XNmiKwpAMFoAAHP gAAABG Template User Talk Pages From the free encyclopedia Jump to navigation Jump to v e User Talk Pages User talk pages Usertalkpage User talk Usertalkback Userwhisperback Talk header preload Message Talkpagecool User notification preference Notification preferences NP Usertalkpage rounded User talk rules User talk top Usercomment Usertalkconcise Talk header User talk header Usertalksuper Usertalkpage blue User mbox Category Template documentation Initial visibility currently defaults to To this template initial visibility the parameter may be used statecollapsed User Talk Pages')
Excl.add_to_exclusion_list(r'Template Csmall Multiple issues Statistics Template Template Multiple issues Multiple issues template protected templates using small message boxes Exclude in print message templates message templates missing parameters Templates used by Twinkle Templates used by AutoWikiBrowser Lua based templates Templates using TemplateData templates Templates that add tracking category January February March April May June July August September October November December Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Template Multiple issues templateeditor templateeditor templateData templateData images inputBox ui input ui checkbox oojs ui core oojs ui indicators oojs ui textures widgets oojs ui icons oojs ui icons alerts oojs ui icons interactions jquery makeCollapsible ui jquery tablesorter jquery makeCollapsible Template Multiple issues From the free encyclopedia Jump to navigation Jump to This article has multiple issues Please help improve it or discuss')
Excl.add_to_exclusion_list(r'shortcutboxplain solid aaa fff em padding em em em em shortcutlist inline block bottom solid aaa bottom em normal shortcutanchordiv position relative top em Shortcuts WP REFB WP REFBEGIN WP REFSTAR ExternalData service geomask maps geoshape getgeojson idsQ properties geomask marker symbol soccer stroke fill opacity marker FF fill FFFFE ExternalData service geoline maps geoline getgeojson idsQ properties geoline marker symbol soccer stroke stroke FF marker FF features Feature geometry')
Excl.add_to_exclusion_list(r'Subcategories subcategories Change links was last changed on Text is available under Creative Commons Attribution Share Alike License GFDL additional terms apply See Terms of Use for details Privacy policy About Disclaimers Developers Cookie statement Mobile About Disclaimers Contact Developers Cookie statement Mobile Lang es Reflist web Text is available under Creative Commons Attribution ShareAlike License additional terms apply By you agree Terms of Use Privacy Policy is registered trademark of Wikimedia Foundation Inc non profit organization Privacy policy About Disclaimers Contact Developers Cookie statement Mobile Infobox settlement Infobox Coord Infobox settlement areadisp Infobox settle Hidden categories Noindexed Navigation menu Personal tools Not logged')
Excl.add_to_exclusion_list(r'HDI Area Database Global Data Lab hdi globaldatalab Retrieved citation citation q quotes citation lock Lock green Lock green citation lock limited citation lock Lock gray Lock gray citation lock Lock red Lock red code code')
Excl.add_to_exclusion_list(r'Wanted files files Media statistics Differences Permanent link Random Random root Redirect revision log ID simpan VIPS scaling test pamanintun MIME API feature usage API sandbox Abuse filter configuration Wanted Lists tree group rights List OAuth applications List globally blocked IP addresses Membership global groups Notifications quiet hover main quiet focus main footer quiet hover main footer quiet focus ad headline number media min main rem rem rem media min main wrapper rem main wrapper rem main rem rem rem media min main wrapper main wrapper main wrapper main wrapper main rem rem rem main p main main ul rem main quiet main main articleCount skin minerva main articleCount main mobileSearch rem skin minerva main mobileSearch main mobileSearchButton shadow rgba media min main f f fa ccd radius shadow rgba rem rem main ul main articleCount rem skin minerva main articleCount skin minerva main mobileSearch media min main letters banner rem rem rem main linear gradient f f fa f f fa rgba rem rem rem main main ul reverse main createArticle li quiet skin modern main line rem rem')
Excl.add_to_exclusion_list(r'b ISO RLCONF posterDirected retrieved b ISO retrieved b ISO retrieved b ISO retrieved b ISO retrieved featured mySandbox AdvancedSiteNotices datePublished T Z dateModified T Z Timezones B B author Organization Contributors projects publisher Organization ImageObject static wmf')
Excl.add_to_exclusion_list(r'deprecated syntax pygments Module Check unknown Module history purge avoid large scale disruption unnecessary server any changes should first tested modules testcases')
Excl.add_to_exclusion_list(r'feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic ene feb mar abr jun jul ago sep oct nov dic jueves mayo mayo Lu Ma Mi Ju Vi Sa Do')
Excl.add_to_exclusion_list(r'nl januari februari maart april mei juni juli augustus september oktober november december jan feb mrt apr mei jun jul aug sep okt nov dec mei XN nl nl Nederlands Direct ProtectionTemplates InterProjectLinks ')
Excl.add_to_exclusion_list(r'Januar Februar März Mai Juni Juli Oktober Dezember Mär Mai Okt Dez er er er er er er er Januar Kw Mo Di Mi Do Fr Sa So Februar Kw Mo Di Mi Do Fr Sa So März Kw Mo Di Mi Do Fr Sa So Kw Mo Di Mi Do Fr Sa So Mai Kw Mo Di Mi Do Fr Sa So Juni Kw Mo Di Mi Do Fr Sa So Juli Kw Mo Di Mi Do Fr Sa So Kw Mo Di Mi Do Fr Sa So Kw Mo Di Mi Do Fr Sa So Oktober Kw Mo Di Mi Do Fr Sa So Kw Mo Di Mi Do Fr Sa So Dezember Kw Mo Di Mi Do Fr Sa So')
Excl.add_to_exclusion_list(r'XNu Nq cAAACP nl nl nl januari februari maart april mei juni juli augustus september oktober november december jan feb mrt apr mei jun jul aug sep okt nov dec ')
Excl.add_to_exclusion_list(r'Januarie Februarie Maart Mei Junie Julie Augustus Oktober Desember Mrt Mei Sept Okt Des  Aa Ab Ac Ad Ae Af Ag Ah Ai Aj Ak Al Am An Ao Ap Aq Ar As At Au Av Aw Ax Ay Az Ba Bb Bc Bd Be Bf Bg Bh Bi Bj Bk Bl Bm Bn Bo Bp Bq Br Bs Bt Bu Bv Bw Bx Bz Cb Cc Cd Ce Cf Cg Ch Cj Ck Cl Cm Cn Co Cq Cr Cs Ct Cu Cv Cw Cx Cy Cz Da Db Dc Dd De Df Dg Dh Dj Dk Dl Dm Dn Dp Dq Dr Ds Dt Du Dv Dw Dx Dy Dz Ea Eb Ec Ed Ee Ef Eg Eh Ei Ej Ek El Em En Eo Ep Eq Er Es Et Eu Ev Ew Ex Ey Ez Fa Fb Fc Fd Fe Ff Fg Fh Fi Fj Fk Fl Fm Fn Fo Fp Fq Fs Ft Fu Fv Fw Fx Fy Fz Ga Gb Gc Gd Ge Gf Gg Gh Gi Gj Gk Gl Gm Gn Go Gp Gq Gr Gs Gt Gu Gv Gw Gx Gy Gz Ha Hb Hc Hd He Hf Hg Hh Hi Hj Hk Hl Hm Hn Ho Hp Hq Hr Hs Ht Hu Hv Hw Hx Hy Hz Ia Ib Ic Id Ie If Ig Ih Ii Ij Ik Il Im In Io Ip Iq Ir Is It Iu Iv Iw Ix Iy Iz Ja Jb Jc Jd Je Jf Jg Jh Ji Jj Jk Jl Jm Jn Jo Jp Jq Jr Js Jt Jv Jw Jx Jy Jz Ka Kb Kc Kd Ke Kf Kg Kh Ki Kj Kk Kl Km Kn Ko Kp Kq Kr Ks Kt Ku Kv Kx Ky Kz La Lb Lc Ld Le Lf Lg Lh Li Lj Lk Ll Lm Ln Lo Lp Lq Lr Ls Lt Lv Lw Lx Ly Lz Mb Mc Md Me Mf Mg Mh Mj Mk Ml Mm Mn Mp Mq Mr Ms Mt Mu Mv Mw Mx My Mz Na Nb Nc Nd Ne Nf Ng Nh Ni Nj Nk Nl Nm Nn No Np Nr Ns Nt Nu Nv Nw Nx Ny Nz Oa Ob Oc Od Oe Of Og Oh Oi Oj Ok Ol Om Oo Op Oq Or Os Ot Ou Ov Ow Ox Oy Oz Pa Pb Pc Pd Pe Pf Pg Ph Pi Pj Pk Pl Pm Pn Po Pp Pq Pr Ps Pt Pu Pv Pw Px Py Pz Qa Qb Qc Qd Qe Qf Qg Qh Qi Qj Qk Ql Qm Qn Qo Qp Qq Qr Qs Qt Qu Qv Qw Qx Qy Qz Ra Rb Rc Rd Re Rf Rg Rh Ri Rj Rk Rl Rm Rn Ro Rp Rq Rr Rs Rt Ru Rv Rw Rx Ry Rz Sb Sc Sd Se Sf Sg Sh Si Sj Sk Sl Sm Sn Sp Sq Sr Ss St Su Sv Sw Sx Sy Sz Ta Tb Tc Td Te Tf Tg Th Tj Tk Tl Tm Tn Tp Tq Tr Ts Tt Tu Tv Tw Tx Ty Tz Ua Ub Uc Ud Ue Uf Ug Uh Ui Uj Uk Ul Um Un Uo Up Uq Ur Us Ut Uu Uv Uw Ux Uy Uz Va Vb Vc Vd Ve Vf Vg Vh Vj Vk Vl Vm Vn Vo Vp Vq Vr Vs Vt Vu Vv Vw Vx Vy Vz Wa Wb Wc Wd We Wf Wg Wh Wi Wj Wk Wl Wm Wn Wo Wp Wq Wr Ws Wt Wu Wv Ww Wx Wy Wz Xa Xb Xc Xd Xe Xf Xg Xh Xi Xj Xk Xl Xm Xn Xo Xp Xq Xr Xs Xt Xu Xv Xw Xx Xy Xz Ya Yb Yc Yd Ye Yf Yg Yh Yi Yj Yk Yl Ym Yn Yo Yp Yq Yr Ys Yt Yu Yv Yw Yx Yy Yz Za Zb Zc Zd Ze Zf Zg Zh Zi Zj Zk Zl Zm Zn Zo Zp Zq Zr')
Excl.add_to_exclusion_list(r'XN AAJt wAAABS wq A F G H I J K M O R S U V W Y NavFrame NavFrame NavPic NavHead EAECF NavFrame after NavFrame NavFrame NavFrame NavFrame NavToggle')
Excl.add_to_exclusion_list(r'Januar Februar März Mai Juni Juli Oktober Dezember Mär Mai Okt Dez Hauptseite XN tRA thin')
Excl.add_to_exclusion_list(r'fr fr damaging string fullCoverage filters likelygood label ores rcfilters damaging likelygood label ores rcfilters damaging likelygood desc cssClass changeslist damaging likelygood priority subset conflicts defaultHighlightColor maybebad label ores rcfilters damaging maybebad label ores rcfilters damaging maybebad desc cssClass changeslist damaging maybebad priority subset damaging likelybad damaging verylikelybad conflicts defaultHighlightColor likelybad label ores rcfilters damaging likelybad label ores rcfilters damaging likelybad desc low cssClass changeslist damaging likelybad priority subset damaging verylikelybad conflicts defaultHighlightColor verylikelybad label ores rcfilters damaging verylikelybad label ores rcfilters damaging verylikelybad desc cssClass changeslist damaging verylikelybad priority subset conflicts defaultHighlightColor priority conflicts changeType hidelog globalDescription ores rcfilters ores conflicts logactions contextDescription ores rcfilters damaging conflicts logactions changeType hideWikibase globalDescription rcfilters hide conflicts ores contextDescription rcfilters damaging conflicts hide whatsThisHeader ores rcfilters damaging whats whatsThisBody ores rcfilters damaging whats whatsThisUrl Special MyLanguage Help New filters review Quality Intent Filters whatsThisLinkText ores rcfilters whats ores rcfilters damaging separator default goodfaith string fullCoverage filters likelygood label ores rcfilters goodfaith good label ores rcfilters goodfaith good desc cssClass changeslist goodfaith good priority subset conflicts defaultHighlightColor maybebad label ores rcfilters goodfaith maybebad label ores rcfilters goodfaith maybebad desc cssClass changeslist goodfaith maybebad priority subset goodfaith likelybad goodfaith verylikelybad conflicts defaultHighlightColor likelybad label ores rcfilters goodfaith bad label ores rcfilters goodfaith bad desc low cssClass changeslist goodfaith bad priority subset goodfaith verylikelybad conflicts defaultHighlightColor verylikelybad label ores rcfilters goodfaith verylikelybad label ores rcfilters goodfaith verylikelybad desc cssClass changeslist goodfaith verylikelybad priority subset conflicts defaultHighlightColor priority conflicts changeType hidelog globalDescription ores rcfilters ores conflicts logactions contextDescription ores rcfilters goodfaith conflicts logactions changeType hideWikibase globalDescription rcfilters hide conflicts ores contextDescription rcfilters goodfaith conflicts hide whatsThisHeader ores rcfilters goodfaith whats whatsThisBody ores rcfilters goodfaith whats whatsThisUrl Special MyLanguage Help New filters review Quality Intent Filters whatsThisLinkText ores rcfilters whats ores rcfilters goodfaith separator default userExpLevel string fullCoverage filters unregistered label rcfilters experience level unregistered label rcfilters experience level unregistered cssClass changeslist unregistered priority subset conflicts defaultHighlightColor label rcfilters experience level label rcfilters experience level cssClass changeslist priority subset userExpLevel newcomer userExpLevel learner userExpLevel experienced conflicts defaultHighlightColor newcomer label rcfilters experience level newcomer label rcfilters experience level newcomer cssClass changeslist newcomer priority subset conflicts defaultHighlightColor learner label rcfilters experience level learner label rcfilters experience level learner cssClass changeslist learner priority subset conflicts defaultHighlightColor experienced label rcfilters experience level experienced label rcfilters experience level experienced fr janvier février mars avril mai juin juillet aot septembre octobre novembre décembre janv fév mars avr mai juin juill aot sept oct nov déc ')
Excl.add_to_exclusion_list(r'Mga Mga bag Lint errors Mga redirect nga Mga redirect nga not connected fewest revisions without language Protected Protected titles Uncategorized Disambiguation Entity linking disambiguation topics near property badges Tracking Login create account account rename request Login unification status Users Active users Autoblocks Blocked users Bot passwords credentials remove email address account manager accounts management Grants Mga Password policies Remove credentials Reset password Recent changes logs Valid change reports uploads File nga Search duplicate N L w D')
Excl.add_to_exclusion_list(r'januar februar marts april maj juni juli august september oktober november december jan feb mar apr maj jun jul aug sep okt nov dec Ma Ti On Fr Lø Sø januar februar marts april maj juni juli august september oktober november december jan feb mar apr maj jun jul aug sep okt nov dec maj lat lon emfh redirect NewSection ')
Excl.add_to_exclusion_list(r' OpenStreetMapFrame  ArchiveLinks MonobookToolbarStandard Wdsearch Cp empty SimilarTitles PDCStriker TMHGalleryHook HiddenCat ExternalSearch Form')
Excl.add_to_exclusion_list(r'Janewoore Febrewoore Marts Jüüne Jüüle Oktoober Nofember Detsember Nof Det gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre dicembre gen mag giu lug ott nomobile Cspan')
Excl.add_to_exclusion_list(r'Eneru Pebreru Marsu Abril Mayu Juniu Juliu Agostu Setyembri Oktubri Nobyembri Disyembri Ene Peb Mrs Abr Myu Hnu Hul Ago Set Nob Dis ')
Excl.add_to_exclusion_list(r'Enero Pebrero Marso Mayo Hunyo Hulyo Agosto Septyembre Oktubre Nobyembre Disyembre Mayo Hun Internet country domain hlCountry domains ae ag ai al am an ao aq ar as au aw ax az ba bb bd bf bg bh bi bj bm bn bo br bs bt bw bz ca cd cf cg ch ci ck cl cm cn co cr cu cv cx cy cym cz dj dk dm do dz ec ee eg et eu fi fj fk fm fo ga gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu ie il im io iq ir je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc lk lr ls lt lu lv ly ma mc md me mg mh mk ml mm mn mo mp mq mr ms mt mu mv mx my mz na nc ne nf ni np nr nu nz om pa pe pf pg ph pk pl pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sk sl sm sn sr st su sv sy sz tc tf tg th tj tk tl tm tn tt tv tw tz ua ug uk us uy uz va vc ve vg vi vn vu wf ye za zm zwInternationalized IDN ccTLD')
Excl.add_to_exclusion_list(r'ae ag ai al am an ao aq ar as au aw ax az ba bb bd bf bg bh bi bj bm bn bo br bs bt bw bz ca cd cf cg ch ci ck cl cm cn co cr cu cv cx cy cym cz dj dk dm do dz ec ee eg et eu fi fj fk fm fo ga gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu ie il im io iq ir je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc lk lr ls lt lu lv ly ma mc md me mg mh mk ml mm mn mo mp mq mr ms mt mu mv mx my mz na nc ne nf ni np nr nu nz om pa pe pf pg ph pk pl pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sk sl sm ')
Excl.add_to_exclusion_list(r'mart septembar oktobar novembar decembar filtergroup authorship send unselected hidemyself editsbyself editsbyself hidebyothers editsbyother editsbyother others filtergroup authorship automated send unselected hidebots bots bots bot hidehumans humans humans human filtergroup automated significance send unselected hideminor minor minor minor hidecategorization hideminor typeofchange hideminor typeofchange hideminor typeofchange hideminor typeofchange hidenewpages hideminor typeofchange hideminor typeofchange hidemajor major major major major major filtergroup significance lastRevision send unselected hidelastrevision lastrevision lastrevision hidepreviousrevisions previousrevision previousrevision previous filtergroup lastRevision send unselected hidepageedits pageedits pageedits hidenewpages newpages newpages new significance hideminor hideminor typeofchange typeofchange hideminor hidecategorization categorization categorization categorize significance hideminor hideminor typeofchange typeofchange hideminor significance hidemajor major major significance hideminor hideminor typeofchange typeofchange hideminor filtergroup changetype wgStructuredChangeFiltersMessages')
Excl.add_to_exclusion_list(r'Ci Ci HjC lp ELs her i WikidataPageBanner TxikipediaTab positionBanner Cul gallery gallery packed overlay Cli gallerybox auto Banner gif Banner gif ')
Excl.add_to_exclusion_list(r'Aa Ab Ac Ad Ae Af Ag Ah Ai Aj Ak Al Am An Ao Ap Aq Ar As At Au Av Aw Ax Ay Az Ba Bb Bc Bd Be Bf Bg Bh Bi Bj Bk Bl Bm Bn Bo Bp Bq Br Bs Bt Bu Bv Bw Bx Bz Cb Cc Cd Ce Cf Cg Ch Cj Ck Cl Cm Cn Co Cq Cr Cs Ct Cu Cv Cw Cx Cy Cz Da Db Dc Dd De Df Dg Dh Dj Dk Dl Dm Dn Dp Dq Dr Ds Dt Du Dv Dw Dx Dy Dz Ea Eb Ec Ed Ee Ef Eg Eh Ei Ej Ek El Em En Eo Ep Eq Er Es Et Eu Ev Ew Ex Ey Ez Fa Fb Fc Fd Fe Ff Fg Fh Fi Fj Fk Fl Fm Fn Fo Fp Fq Fs Ft Fu Fv Fw Fx Fy Fz Ga Gb Gc Gd Ge Gf Gg Gh Gi Gj Gk Gl Gm Gn Go Gp Gq Gr Gs Gt Gu Gv Gw Gx Gy Gz Ha Hb Hc Hd He Hf Hg Hh Hi Hj Hk Hl Hm Hn Ho Hp Hq Hr Hs Ht Hu Hv Hw Hx Hy Hz Ia Ib Ic Id Ie If Ig Ih Ii Ij Ik Il Im In Io Ip Iq Ir Is It Iu Iv Iw Ix Iy Iz Ja Jb Jc Jd Je Jf Jg Jh Ji Jj Jk Jl Jm Jn Jo Jp Jq Jr Js Jt Jv Jw Jx Jy Jz Ka Kb Kc Kd Ke Kf Kg Kh Ki Kj Kk Kl Km Kn Ko Kp Kq Kr Ks Kt Ku Kv Kx Ky Kz La Lb Lc Ld Le Lf Lg Lh Li Lj Lk Ll Lm Ln Lo Lp Lq Lr Ls Lt Lv Lw Lx Ly Lz Mb Mc Md Me Mf Mg Mh Mj Mk Ml Mm Mn Mp Mq Mr Ms Mt Mu Mv Mw Mx My Mz Na Nb Nc Nd Ne Nf Ng Nh Ni Nj Nk Nl Nm Nn No Np Nr Ns Nt Nu Nv Nw Nx Ny Nz Oa Ob Oc Od Oe Of Og Oh Oi Oj Ok Ol Om Oo Op Oq Or Os Ot Ou Ov Ow Ox Oy Oz Pa Pb Pc Pd Pe Pf Pg Ph Pi Pj Pk Pl Pm Pn Po Pp Pq Pr Ps Pt Pu Pv Pw Px Py Pz Qa Qb Qc Qd Qe Qf Qg Qh Qi Qj Qk Ql Qm Qn Qo Qp Qq Qr Qs Qt Qu Qv Qw Qx Qy Qz Ra Rb Rc Rd Re Rf Rg Rh Ri Rj Rk Rl Rm Rn Ro Rp Rq Rr Rs Rt Ru Rv Rw Rx Ry Rz Sb Sc Sd Se Sf Sg Sh Si Sj Sk Sl Sm Sn Sp Sq Sr Ss St Su Sv Sw Sx Sy Sz Ta Tb Tc Td Te Tf Tg Th Tj Tk Tl Tm Tn Tp Tq Tr Ts Tt Tu Tv Tw Tx Ty Tz Ua Ub Uc Ud Ue Uf Ug Uh Ui Uj Uk Ul Um Un Uo Up Uq Ur Us Ut Uu Uv Uw Ux Uy Uz Va Vb Vc Vd Ve Vf Vg Vh Vj Vk Vl Vm Vn Vo Vp Vq Vr Vs Vt Vu Vv Vw Vx Vy Vz Wa Wb Wc Wd We Wf Wg Wh Wi Wj Wk Wl Wm Wn Wo Wp Wq Wr Ws Wt Wu Wv Ww Wx Wy Wz Xa Xb Xc Xd Xe Xf Xg Xh Xi Xj Xk Xl Xm Xn Xo Xp Xq Xr Xs Xt Xu Xv Xw Xx Xy Xz Ya Yb Yc Yd Ye Yf Yg Yh Yi Yj Yk Yl Ym Yn Yo Yp Yq Yr Ys Yt Yu Yv Yw Yx Yy Yz Za Zb Zc Zd Ze Zf Zg Zh Zi Zj Zk Zl Zm Zn Zo Zp Zq Zr Zs Zt Zu Zv Zw Zx Zy Zz')
Excl.add_to_exclusion_list(r'dd yyyy y z y y o z z xx lambda yy lambda   zz lambda wgStructuredChangeFiltersCollapsedState StructuredChangeFiltersDisplayConfig maxDays limitArray limitDefault daysArray daysDefault wgStructuredChangeFiltersSavedQueriesPreferenceName saved queries wgStructuredChangeFiltersLimitPreferenceName wgStructuredChangeFiltersDaysPreferenceName rcdays wgStructuredChangeFiltersCollapsedPreferenceName rc collapsed oresData oresThresholds css legend base feedlink legend ')
Excl.add_to_exclusion_list(r'g r r sum frac g r frac r Therefore g r g g r g g r r g frac g r g frac g r frac g g infty r r g Aa Ae Aj Ao At Ba Be Bj Bo Bt Ce Cj Co Ct Da De Dj Dt Ea Ee Ej Eo Et Fa Fe Fj Fo Ft Ga Ge Gj Go Gt Ha He Hj Ho Ht Ia Ie Ij Io It Ja Je Jj Jo Jt Ka Ke Kj Ko Kt La Le Lj Lo Lt Me Mj Mt Na Ne Nj No Nt Oa Oe Oj Oo Ot Pa Pe Pj Po Pt Qa Qe Qj Qo Qt Ra Re Rj Ro Rt Se Sj St Ta Te Tj Tt Ua Ue Uj Uo Ut Va Ve Vj Vo Vt Wa We Wj Wo Wt Xa Xe Xj Xo Xt Ya Ye Yj Yo Yt Za Ze Zj Zo Zt ')
Excl.add_to_exclusion_list(r'IABot wgFlaggedRevsEditLatestRevision j BC Januari Februari Mac Julai Ogos Disember CS')

# An appender which strips the html from unnecessary content
# Appends the text to a csv for storage
class CsvAppender:
    re_en = re.compile(r'\bhttps\:\/\/(www\.){0,1}(en|simple)\.wikipedia\.org')
    re_de = re.compile(r'\bhttps\:\/\/(www\.){0,1}de\.wikipedia\.org')
    re_x = re.compile(r'\bhttps\:\/\/(www\.){0,1}(es|bs|da|ms|fi|fr|it|sv|pam|af|frr|nl|ceb|war|eu)\.wikipedia\.org')

    def __init__(self, target_file, minMaxLen):
        self.target_file = target_file
        self.minMaxLen = minMaxLen

    def getLang(url):
        if (url is None):
            return None
        
        if (CsvAppender.re_de.search(url) is not None):
            return 'G'
        elif (CsvAppender.re_en.search(url) is not None):
            return 'E'
        elif (CsvAppender.re_x.search(url) is not None):
            return 'X'

        return None
        
    def append(self, url, html):
        
        lang = CsvAppender.getLang(url)
        if (lang is None):
            return False

        # remove space sequences
        html = Excl.clean(html)[:self.minMaxLen[1]]

        if (len(html) < self.minMaxLen[0] or html is ''):
            return False

        # Then store the text at the end of the existing csv or create it
        with Path(self.target_file) as file_p:
            if (not file_p.exists()):
                with open(self.target_file, 'w', encoding='utf-8') as file_w:
                    file_w.write('language;url;text\n')
                    file_w.close()
        
        with open(self.target_file, 'a', encoding='utf-8') as file:
            file.write(lang + ';' + url + ';' + html + '\n')
            file.close()

        return True

def clean_csv(file_name):
    csv = pandas.read_csv(file_name, sep=';')
    languages = csv['language']
    urls = csv['url']
    texts = csv['text']

    csvAppender = CsvAppender('cleaned')

    for it in range(len(texts)):
        Crawler.animate_work()
        texts[it] = Excl.stripHtml(texts[it])
        csvAppender.append(url=urls[it], html=texts[it])

class LinkParser(HTMLParser):

    def __init__(self, links_only):
        super().__init__()
        self.links_only = links_only


    re_type_html = re.compile(r'(text\/html\;)')

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    self.links = self.links + [newUrl]

    def handle_data(self, data):
        if (self.links_only):
            return
        # Strip text that is unusable remove any new line characters (replace with space)
        self.innerText += Excl.stripHtml(data)

    def getLinks(self, url):
        self.links = []
        self.innerText = ""
        self.baseUrl = url

        with urlopen(url) as response:
            if LinkParser.re_type_html.match(response.getheader('Content-Type')) is not None:
                htmlBytes = response.read()
                self.htmlString = htmlBytes.decode("utf-8")
                self.feed(self.htmlString)
                response.close()
                return self.innerText, self.links
            else:
                response.close()
                return "",[]

def parse_url(args):
    url = args.url
    parser = LinkParser(links_only=args.links_only)
    inner_text, links = parser.getLinks(url)
    return (url, inner_text, links)

class WorkerArgs:
    def __init__(self, url, links_only):
        self.url = url
        self.links_only = links_only

class TaskManager:

    def __init__(self, max_tasks, workers):
        self.max_tasks = max_tasks
        self.tasks = []
        self.pool = Pool(workers)

    def any_ready(self):
        for t in self.tasks:
            if (t.ready()):
                return t.ready()
        return False

    def get_ready_task(self):
        for it in range(len(self.tasks)):
            if (self.tasks[it].ready()):
                task = self.tasks[it]
                self.tasks = self.tasks[:it] + self.tasks[it+1:] # list(filter(lambda t: not t is task, self.tasks))
                return task
        return None
    
    def full(self):
        return len(self.tasks) >= self.max_tasks
    def empty(self):
        return len(self.tasks) is 0
    
    def put(self, func, args_tuple):
        if (len(self.tasks) < self.max_tasks):
            async_result = self.pool.apply_async(func, [args_tuple])
            self.tasks.append(async_result)
            return async_result
        return None

    def count(self):
        return len(self.tasks)

class Crawler():

    re_valid_url = re.compile(r'\bhttps\:\/\/(www\.){0,1}(en|simple|de|es|bs|da|ms|fi|fr|it|pam|af|frr|nl|ceb|war|eu)\.wikipedia\.org')
    re_is_not_article = re.compile(r'[#?=]|(Wikipedia:)|(\.svg)|(\.jpg)|(\.png)|(\.gif)|(\.mp4)|(\.tiff)|(\.bmp)|(https:/[^\/])|(http:/[^\/])')
    anim_idx = 0
    anim = "/–\\|"
    anim_calls = 0

    def __init__(self, write_html_to='CrawledPages.csv', state_file='Crawler.state', maxPages=10000, resume=False, minMaxLen=(3000, 4000), num_workers=0):
        self.main = False
        self.pagesVisited = []
        self.write_to = write_html_to
        self.state_file = state_file
        self.pagesToVisit = []
        self.maxPages = maxPages
        self.keyboard_interrupt = False
        self.trash_pages = set([])
        self.minMaxLen = minMaxLen
        self.num_workers = num_workers

        try:
            with open(state_file, 'rb') as file:
                state = Crawler.mapState(pickle.load(file), '4')
                if (resume):
                    self.pagesToVisit = state['d']['pages_to_visit']
                self.trash_pages = state['d']['trash_pages']
                file.close()
        except:
            try: # Old standard State file 
                with open('Spider.state', 'rb') as file:
                    state = Crawler.mapState(pickle.load(file), '4')
                    if (resume):
                        self.pagesToVisit = state['d']['pages_to_visit']
                    self.trash_pages = state['d']['trash_pages']
                    file.close()
            except:
                print('Did not load state from: ', state_file)
        try:
            csv = pandas.read_csv(self.write_to, sep=';', encoding='utf-8')
            self.pagesVisited = list(csv['url'])
            if (resume):
                self.pagesToVisit.append(self.pagesVisited[-1:][0])
        except IOError as e:
            print('A csv has not yet been created. Did not load visited pages from: ', self.write_to, e)
        print('Crawler visited ', len(self.pagesVisited), 'pages')

        os_cpu_count = os.cpu_count()
        if (self.num_workers == 0): self.num_workers = 2
        if (self.num_workers >= os_cpu_count - 1): self.num_workers = os_cpu_count - 1
        if (self.num_workers <= 0): self.num_workers = 1
        self.max_tasks = ceil(self.num_workers * 1.25) + 2

    def ignore_page(self, url):
        return url is None or (url in self.pagesVisited) or (url in self.trash_pages) or Crawler.re_valid_url.match(url) is None or not Crawler.re_is_not_article.search(url) is None

    '''
    Start crawling wikipedia. Exit with CTRL+C (for Linux and Windows).
    '''
    def crawl(self, maxPages=None, write_html_to=None):

        self.tasks = TaskManager(max_tasks=self.max_tasks, workers=self.num_workers)
        self.main = True
        self.cprint(custom='Using ' + str(self.num_workers) + ' workers queuing up to ' + str(self.max_tasks) + ' tasks', end='\n')

        if (write_html_to is None):
            write_html_to = self.write_to
        if (maxPages is None):
            maxPages = self.maxPages
        
        csvAppender = CsvAppender(write_html_to, self.minMaxLen)
        do_save_state = 0

        while (not self.tasks.empty() or (len(self.pagesToVisit) > 0 and not self.keyboard_interrupt)):
            try:
                # push next url if pending results list is free
                if (not self.keyboard_interrupt and not self.tasks.full() and len(self.pagesToVisit) > 0):
                    Crawler.animate_work(True)
                    url = self.pagesToVisit[0]
                    self.pagesToVisit = self.pagesToVisit[1:]
                    self.tasks.put(parse_url, WorkerArgs(url, self.ignore_page(url)))

                Crawler.animate_work(True)
                if (self.keyboard_interrupt):
                    self.cprint(custom='')

                # pull a result if tasks not empty and a task is ready
                if (not self.tasks.empty() and self.tasks.any_ready()):
                    try:
                        url, innerText, links = self.tasks.get_ready_task().get()
                    except Exception as e:
                        self.cprint(error=e, url=url, end='\n')
                        continue
                    
                    self.cprint(steps=[2], url=url)

                    links = list([l for l in links if not self.ignore_page(l)])
                    
                    Crawler.animate_work(True, times=2)

                    # append html to file
                    if (not self.ignore_page(url)):
                        Crawler.animate_work(True)
                        self.cprint(steps=[3], url=url)
                        appended = csvAppender.append(url, innerText)
                        Crawler.animate_work(True, times=2)
                        if appended:
                            self.pagesVisited.append(url)
                            self.cprint(steps=[4], url=url)
                        else:
                            self.cprint(steps=[5], url=url, end='\n')
                            self.trash_pages.add(url)
                    else:
                        self.cprint(steps=[5], url=url, end='\n')
                        self.trash_pages.add(url)

                    Crawler.animate_work(True)

                    # Add the pages that we should visit next to the end of our collection
                    # of pages to visit:
                    random.shuffle(links)
                    Crawler.animate_work(True)

                    weight = 5
                    lang = CsvAppender.getLang(url)
                    if (lang is 'G' or lang is 'E'): weight = 6
                    
                    links = links[:weight]
                    self.pagesToVisit = self.pagesToVisit + links
                    Crawler.animate_work(True)
                    random.shuffle(self.pagesToVisit)
                    self.pagesToVisit = self.pagesToVisit[:300]
                    Crawler.animate_work(True)
        
            except KeyboardInterrupt as ki:
                self.handle_keyboard_interrupt()

        # save state before exiting
        self.saveState()
        print('\n\n')
        
    '''
    Mapping state to different versions
    Mapping down may lead to loss of state variables
    '''
    def mapState(src, targetVersion):

        srcVersion = src['v']

        print('map state version ' + str(srcVersion) + ' to ' + str(targetVersion))

        pagesVisited = []
        pagesToVisit = []
        trash_pages = set([])

        if (srcVersion is targetVersion):
            return src

        if (srcVersion is '1'):
            pagesVisited = src['d']
        if (srcVersion is '2'):
            pagesVisited = src['d']['pv']
            pagesToVisit = src['d']['tv']
        if (srcVersion is '3'):
            pagesToVisit = src['d']['pages-to-visit']
        if (srcVersion is '4'):
            pagesToVisit = src['d']['pages_to_visit']
            trash_pages = src['d']['trash_pages']
        
        if (targetVersion is '1'):
            return {
                'v': '1',
                'd': pagesVisited
            }
        if (targetVersion is '2'):
            return {
                'v': '2',
                'd': {
                    'pv': pagesVisited,
                    'tv': pagesToVisit
                }
            }
        if (targetVersion is '3'):
            return {
                'v': '3',
                'd': {
                    'pages-to-visit': pagesToVisit
                }
            }
        if (targetVersion is '4'):
            return {
                'v': '4',
                'd': {
                    'pages_to_visit': pagesToVisit,
                    'trash_pages': set(trash_pages)
                }
            }
        
        return src
        
    '''
    Save state as binary
    '''
    def saveState(self):
        try:
            with open(self.state_file, 'wb') as file:
                pickle.dump({
                    'v': '4',
                    'd': {
                        'pages_to_visit': self.pagesToVisit,
                        'trash_pages': self.trash_pages
                    }
                }, file)
                file.close()
        except:
            print('Could not save state to: ', self.state_file)

    '''
    Creates and animation like {/} > {–} > {\} > {|}
    '''
    def animate_work(force=False, times=1, delay=.14, empty=False):
        Crawler.anim_calls = (Crawler.anim_calls + 1) % 50
        newAnim = Crawler.anim_calls is 0
        for i in range(times):
            if (newAnim or force):
                if (delay > .09):
                    time.sleep(delay)
                Crawler.anim_idx += 1
            print_string = '{'
            if (empty):
                print_string += ' '
            else:
                print_string += Crawler.anim[Crawler.anim_idx % len(Crawler.anim)]
            print_string += '}'
            if (newAnim or force):
                print(print_string, end='\r', flush=True)
                # print(print_string, end='\r', flush=True)
        return print_string

    '''
    Append entry point urls
    '''
    def appendUrl(self, url):
        self.pagesToVisit.append(url)

    STEP_MESSAGES = [
        'Page  REQUEST', # 0
        'Page  PARSING', # 1
        'Links FILTER ', # 2
        'Page  SAVING ', # 3
        'Page  SAVE OK', # 4
        'Page  IGNORED', # 5
        'Crawl STOP   ', # 6
        'State SAVE   ', # 7
        'waiting for tasks to finish', # 8
    ]

    def handle_keyboard_interrupt(self, sig=None, frame=None):
        self.keyboard_interrupt = True
        self.cprint(error='KeyboardInterrupt', steps=[6, 7], end='\n')

    def cprint(self, steps=[], url=None, error=None, end='\r', flush=True, custom=''):
        if (not self.main):
            return 0
            
        print('\r', end='\r')
        
        print_string = ''
        work_anim = Crawler.animate_work(empty=( (5 in steps) or ('\n' in end) or ('\n' in custom) ))

        kb_interrupt_message = ' (' + Crawler.STEP_MESSAGES[8] + ' : ' + str(self.tasks.count()) + ' remaining ) '

        if (len(custom) > 0):
            print_string += work_anim + ' '
            if (self.keyboard_interrupt):
                print_string += kb_interrupt_message + ' '
            if (not custom is None and not custom == ''):
                print_string += ' - ' + custom
        else:
            if (not error is None):
                print_string = str(error) + ': '
            else:
                print_string = work_anim + ' '
                print_string += str(len(self.pagesVisited) + 1).rjust(5) + ' - '
                if (self.keyboard_interrupt):
                    print_string += kb_interrupt_message + '- '

        if (len(steps) > 0):
            for s in steps:
                print_string += Crawler.STEP_MESSAGES[s] + ' & '
            print_string = print_string[:-2]
            if (not url is None):
                print_string += ': '
        
        lang = CsvAppender.getLang(url)
        if (not lang is None):
            print_string += lang + ' = '
        
        print_string += url or ''

        cols, lines = shutil.get_terminal_size(fallback=(79, 23))
        print_string = print_string.ljust(cols-3)[:cols-3] + '...'

        print(print_string, end=end, flush=flush)

        return print_string

to_csv='Random_Wiki_Pages_2.csv'

# try:
#     clean_csv(to_csv)
# except:
#     print('error while cleaning csv')

crawler = Crawler(resume=False, write_html_to=to_csv, num_workers=1)

def signal_handler(sig, frame):
        crawler.handle_keyboard_interrupt(sig, frame)

signal.signal(signal.SIGINT, signal_handler)

crawler.appendUrl('https://en.wikipedia.org/wiki/Main_Page')
crawler.appendUrl('https://simple.wikipedia.org/wiki/Main_Page')
crawler.appendUrl('https://de.wikipedia.org/wiki/Wikipedia:Hauptseite')
crawler.appendUrl('https://de.wikipedia.org/wiki/Wikipedia:Hauptseite')
crawler.appendUrl('https://da.wikipedia.org/wiki/Forside')
crawler.appendUrl('https://es.wikipedia.org/wiki/Wikipedia:Portada')
crawler.appendUrl('https://bs.wikipedia.org/wiki/Po%C4%8Detna_strana')
crawler.appendUrl('https://frr.wikipedia.org/wiki/Wikipedia:Hoodsid')
crawler.appendUrl('https://af.wikipedia.org/wiki/Tuisblad')
crawler.appendUrl('https://pam.wikipedia.org/wiki/Pun_Bulung')
crawler.appendUrl('https://eu.wikipedia.org/wiki/Azala')
crawler.appendUrl('https://war.wikipedia.org/wiki/Syahan_nga_Pakli')
crawler.appendUrl('https://ceb.wikipedia.org/wiki/Unang_Panid')
crawler.appendUrl('https://sv.wikipedia.org/wiki/Portal:Huvudsida')
crawler.appendUrl('https://nl.wikipedia.org/wiki/Hoofdpagina')
crawler.appendUrl('https://it.wikipedia.org/wiki/Pagina_principale')
crawler.appendUrl('https://ms.wikipedia.org/wiki/Laman_Utama')
crawler.appendUrl('https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal')
crawler.crawl()