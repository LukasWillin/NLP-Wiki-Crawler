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
import random
import pandas
import shutil
import pickle
import sys
import time
import re

class Excl:

    exclusions = set([])
    re_excl_split = re.compile(r'[\t\n\r\ ]')
    re_exclude = None
    
    def add_to_exclusion_list(from_string):
        parts = Excl.re_excl_split.split(from_string)
        for p in parts:
            if (len(p) > 0):
                Excl.exclusions.add(r'(\b' + p + r'\b)|')
        excl_string = r'('
        for e in Excl.exclusions:
            excl_string += e
        excl_string = excl_string[:-1]
        excl_string += r')'
        Excl.re_exclude = re.compile(excl_string)

    re_rem = re.compile(r'[^a-zA-ZäÄöÖüÜëËïÏåÅáÁàÀąĄóÓòÒøØèÈéÉêÊęĘċĊćĆčČùâúÚùÙÂôÔĩĨìÌíÍńŃǹǸñÑłŁƚȽżŻšŠśŚß\ ]|[\']')
    re_space = re.compile(r'[\t\n\r\.\:\;\,\-\_\"\?\!\(\)\{\}\*\@\+\-\<\>\/\\\|0-9]+', flags=re.MULTILINE)
    re_rem_space = re.compile(r'\ {2,}')

    def stripHtml(html):
        # Crawler.animate_work(True)
        html = Excl.re_space.sub(' ', html)
        # Crawler.animate_work(True)
        html = Excl.re_rem.sub('', html)
        # Crawler.animate_work(True)
        return Excl.re_exclude.sub('', html)

    def clean(text):
        return Excl.re_rem_space.sub(' ', text)

        

Excl.add_to_exclusion_list(r'autocollapse statecollapsed wikipedia Wikipedia wpsearch QUERY TERMS ShortSearch document documentElement className most interwikis Page document documentElement className replace      s client nojs  s       client js        titlePunishmentoldid window RLQwindow RLQ    push function   mw config set   wgCanonicalNamespace      wgCanonicalSpecialPageName  false  wgNamespaceNumber     wgPageName   P value   wgTitle   P value   wgCurRevisionId             wgRevisionId             wgArticleId          wgIsArticle  true  wgIsRedirect  false  wgAction   view   wgUserName  null  wgUserGroups       wgCategories ')
Excl.add_to_exclusion_list(r'editWarning wgStructuredChangeFilters Expand Gadget usage statistics Graph sandbox List wikis system sandbox Try hieroglyph markup View interwiki Wiki sets Redirecting special mediawiki action edit collapsibleFooter href  site   mediawiki page startup   mediawiki page ready   mediawiki searchSuggest   ext charinsert   ext gadget teahouse   ext gadget ReferenceTooltips   ext gadget watchlist notice   ext gadget DRN wizard   ext gadget charinsert   ext gadget refToolbar   ext gadget extra toolbar buttons   ext gadget switcher   ext centralauth centralautologin   ext CodeMirror   mmv head   mmv bootstrap autostart   ext popups   ext visualEditor desktopArticleTarget init   ext visualEditor targetLoader   ext eventLogging   ext wikimediaEvents   ext navigationTiming   ext uls compactlinks   ext uls interface   ext quicksurveys init   ext centralNotice geoIP   skins vector js  mw loader load RLPAGEMODULES')
Excl.add_to_exclusion_list(r'mw config set wgInternalRedirectTargetUrl herit inherit inherit inherit cs hidden error cs visible error cs maint aa cs subscription cs registration cs format cs kern cs kern wl cs kern cs kern wl pageneeded wgCanonicalNamespace wgRedirectedFrom Sitenotice title Hjlp sitenotice UTC  wgCanonicalSpecialPageName  false  wgNamespaceNumber     wgPageName   P value   wgTitle   P value   wgCurRevisionId Wikimedia Commons Wikidata index php Creative Commons Attribution ShareAlike License         wgRevisionId             wgArticleId          wgIsArticle  true  wgIsRedirect  false  wgAction   view   wgUserName  null  wgUserGroups td tr tbody table      wgCategories   Articles with short description')
Excl.add_to_exclusion_list(r'wgRelevantPageName wgBackendResponseTime wgHostname wgRelevantArticleId wgSiteNoticeId w titleWikipedia Log Namespaces dismissableSiteNotice cqd ng required helpers helplink htmlform ooui htmlform DateInputWidget userSuggest htmlform htmlform ooui UserInputWidget DateInputWidget thanks corethank   wgRequestId  XNmm QpAIEIAAA SGIAAABD  wgCSPNonce  wgIsProbablyEditable  wgRelevantPageIsProbablyEditable  wgRestrictionEdit  wgRestrictionMove  wgMediaViewerOnClick  wgMediaViewerEnabledByDefault  wgPopupsReferencePreviews  wgPopupsConflictsWithNavPopupGadget  wgVisualEditor  pageLanguageCode  en  pageLanguageDir  ltr  pageVariantFallbacks  en  wgMFDisplayWikibaseDescriptions  search  nearby    tagline   wgRelatedArticles  wgRelatedArticlesUseCirrusSearch  wgRelatedArticlesOnlyUseCirrusSearch  wgWMESchemaEditAttemptStepOversample  wgPoweredByHHVM  wgULSCurrentAutonym  English  wgNoticeProject   wgCentralNoticeCookiesToDelete  wgCentralNoticeCategoriesUsingLegacy  Fundraising  fundraising  wgWikibaseItemId  Q     wgCentralAuthMobileDomain  wgEditSubmitButtonLabelPublish    state   styles    globalCssJs user styles    globalCssJs styles    styles   noscript   user styles    globalCssJs user    globalCssJs    user   user options   user tokens  loading  cite styles    math styles    legacy shared    legacy commonPrint    toc styles   wikibase      noscript    interlanguage    wikimediaBadges    d styles    skinning     styles     implement user tokens tffind  jQuery require module  displaystyle X displaystyle  alpha Leftrightarrow wgPageParseReport limitreport cputime  walltime  ppvisitednodes  limit  ppgeneratednodes  limit  postexpandincludesize  limit  templateargumentsize limit  expansiondepth  limit  expensivefunctioncount  limit unstrip depth  limit  unstrip size  limit  entityaccesscount  limit timingprofile   Templat References    total   Templat Cite journal   Templat Main other scribunto limitreport timeusage   limit   limitreport memusage   limit  cachereport origin timestamp  ttl  transientcontent      context  https  schema  type  Article  name  Nilai url  https  wiki Nilai sameAs  http  www wikidata  entity  mainEntity  nomin  user tokens  editToken     patrolToken     watchToken     csrfToken        cite ux enhancements  math scripts         toc')
Excl.add_to_exclusion_list(r'parser output RLSTATE plainlist ul list main wgIsMainPage tmulti thumbinner display flex flex direction column autoconfirmed sysop wgCoordinates parser output tmulti trow display flex flex direction row clear left flex wrap wrap width  box sizing border box  parser output tmulti tsingle margin px float left  parser output tmulti theader clear both font weight bold text align center align self center background color transparent width  parser output tmulti thumbcaption text align left background color transparent  parser output tmulti text align left text align left  parser output tmulti text align right text align right  parser output tmulti text align center text align center all and max width px parser output tmulti thumbinner width  important box sizing border box max width none important align items center  parser output tmulti trow justify content center  parser output tmulti tsingle float none important max width  important box sizing border box text align center  parser output tmulti thumbcaption text align center')
Excl.add_to_exclusion_list(r'wgBreakFrames wgMonthNamesShort XNjswwpAIEIAAIU iM AAACN LCCN identifiers articles VIAF identifiers articles WorldCat VIAF identifiers Book Compare export  wgFlaggedRevsParams tags accuracy levels  quality  pristine wgStableRevisionId    de  de     Deutsch                   flaggedRevs basic   wzrrbt   variant  de          editMenus  WikiMiniAtlas  OpenStreetMap  CommonsDirekt      categoryPage categoryTree tmh thumbnail xs k af categoryTree MediaWikiPlayer PopUpMediaTransform startUp flaggedRevs advanced classNamedocument  Collider Detector at Fermilab   XNnpDgpAMFQAAJ dO wAAAAK    wgFlaggedRevsParams tags accuracy levels  quality  pristine wgStableRevisionId    de  de     Deutsch Line data file data file td                    flaggedRevs basic   wzrrbt   variant  de            editMenus  WikiMiniAtlas  OpenStreetMap  CommonsDirekt      startUp flaggedRevs advanced var nodedocument getElementById  dismissablenotice anonplace  if node node outerHTML u  Cdiv class  dismissable u  E u  Cdiv class  dismissable close  u  E u  Ca tabindex role button  u  Ezarrar u  C a u  E u  C div u  E u  Cdiv class  dismissable body  u  E u  Cdiv id localNotice  lang ast  dir  u  E u  Ctable style  class noprint plainlinks ambox ambox u  E n u  Ctbody u  E u  Ctr u  E n u  Ctd class ambox image  u  E n u  Cdiv style  u  E u  Cimg alt  src upload wikimedia org commons thumb a ac Noun Project maintenance icon cc svg Noun Project maintenance icon cc svg png  decoding async height  srcset upload wikimedia org commons thumb a ac Noun Project maintenance icon cc svg Noun Project maintenance icon cc svg png x wgPageContentLanguage  de  wgPageContentModel  wikitext  wgSeparatorTransformTable  t t wgDigitTransformTable  wgDefaultDateFormat  dmy  wgMonthNames')
Excl.add_to_exclusion_list(r'templates January span dotted cursor cs ws c Wikisource logo Wikisource logo no repeat wgRelevantUserName bibcoded see bibcode Bibcode February March April May June July August September October November December Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Template User Talk Pages XNmiKwpAMFoAAHP gAAABG Template User Talk Pages From the free encyclopedia Jump to navigation Jump to v e User Talk Pages User talk pages Usertalkpage User talk Usertalkback Userwhisperback Talk header preload Message Talkpagecool User notification preference Notification preferences NP Usertalkpage rounded User talk rules User talk top Usercomment Usertalkconcise Talk header User talk header Usertalksuper Usertalkpage blue User mbox Category Template documentation Initial visibility currently defaults to autocollapse To this template initial visibility the parameter may be used statecollapsed User Talk Pages')
Excl.add_to_exclusion_list(r'Template Csmall Multiple issues Statistics Template Template Multiple issues Multiple issues template protected templates using small message boxes Exclude in print message templates message templates missing parameters Templates used by Twinkle Templates used by AutoWikiBrowser Lua based templates Templates using TemplateData templates Templates that add tracking category January February March April May June July August September October November December Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Template Multiple issues XNnEWApAIC AAKhyJIkAAAAA templateeditor templateeditor templateData templateData images inputBox ui input ui checkbox oojs ui core oojs ui indicators oojs ui textures widgets oojs ui icons oojs ui icons alerts oojs ui icons interactions jquery makeCollapsible ui jquery tablesorter jquery makeCollapsible Template Multiple issues From the free encyclopedia Jump to navigation Jump to This article has multiple issues Please help improve it or discuss')
Excl.add_to_exclusion_list(r'shortcutboxplain solid aaa fff em padding em em em em shortcutlist inline block bottom solid aaa bottom em normal shortcutanchordiv position relative top em Shortcuts WP REFB WP REFBEGIN WP REFSTAR ExternalData service geomask maps geoshape getgeojson idsQ properties geomask marker symbol soccer stroke fill opacity marker FF fill FFFFE ExternalData service geoline maps geoline getgeojson idsQ properties geoline marker symbol soccer stroke stroke FF marker FF features Feature geometry')
Excl.add_to_exclusion_list(r'Subcategories subcategories Change links was last changed on Text is available under Creative Commons Attribution Share Alike License GFDL additional terms apply See Terms of Use for details Privacy policy About Disclaimers Developers Cookie statement Mobile About Disclaimers Contact Developers Cookie statement Mobile Lang es Reflist web Text is available under Creative Commons Attribution ShareAlike License additional terms apply By you agree Terms of Use Privacy Policy is registered trademark of Wikimedia Foundation Inc non profit organization Privacy policy About Disclaimers Contact Developers Cookie statement Mobile Infobox settlement Infobox Coord Infobox settlement areadisp Infobox settle Hidden categories Noindexed Navigation menu Personal tools Not logged')
Excl.add_to_exclusion_list(r'HDI Area Database Global Data Lab hdi globaldatalab Retrieved citation citation q quotes citation lock Lock green Lock green citation lock limited citation lock Lock gray Lock gray citation lock Lock red Lock red code code')
Excl.add_to_exclusion_list(r'Wanted files files Media statistics Tala da reng Differences Permanent link Random Random root Redirect revision log ID simpan VIPS scaling test pamanintun MIME API feature usage API sandbox Abuse filter configuration Wanted Lists tree group rights List OAuth applications List globally blocked IP addresses Membership global groups Notifications quiet hover main quiet focus main footer quiet hover main footer quiet focus ad headline number media min main rem rem rem media min main wrapper rem main wrapper rem main rem rem rem media min main wrapper main wrapper main wrapper main wrapper main rem rem rem main p main main ul rem main quiet main main articleCount skin minerva main articleCount main mobileSearch rem skin minerva main mobileSearch main mobileSearchButton shadow rgba media min main f f fa ccd radius shadow rgba rem rem main ul main articleCount rem skin minerva main articleCount skin minerva main mobileSearch media min main letters banner rem rem rem main linear gradient f f fa f f fa rgba rem rem rem main main ul reverse main createArticle li quiet skin modern main line rem rem')
Excl.add_to_exclusion_list(r'b ISO RLCONF posterDirected retrieved b ISO retrieved b ISO retrieved b ISO retrieved b ISO retrieved featured mySandbox AdvancedSiteNotices datePublished T Z dateModified T Z Timezones B B author Organization Contributors projects publisher Organization ImageObject static wmf')
Excl.add_to_exclusion_list(r'deprecated syntax pygments Module Check unknown Module history purge avoid large scale disruption unnecessary server any changes should first tested modules testcases')

# An appender which strips the html from unnecessary content
# Appends the text to a csv for storage
class CsvAppender:
    re_en = re.compile(r'\bhttps\:\/\/(www\.){0,1}(en|simple)\.wikipedia\.org')
    re_de = re.compile(r'\bhttps\:\/\/(www\.){0,1}de\.wikipedia\.org')
    re_x = re.compile(r'\bhttps\:\/\/(www\.){0,1}(es|bs|da|ms|fi|fr|it|sv|pam|af|frr|nl|ceb|war|eu)\.wikipedia\.org')

    def __init__(self, target_file):
        self.target_file = target_file

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
        html = Excl.clean(html)[:4000]
        
        if (html is ''):
            return False

        Crawler.animate_work(True)

        # Then store the text at the end of the existing csv or create it
        with Path(self.target_file) as file_p:
            if (not file_p.exists()):
                with open(self.target_file, 'w', encoding='utf-8') as file_w:
                    file_w.write('language;url;text\n')
                    file_w.close()
        
        with open(self.target_file, 'a', encoding='utf-8') as file:
            file.write(lang + ';' + url + ';' + html + '\n')
            file.close()

        Crawler.animate_work(True)

        return True

class LinkParser(HTMLParser):

    def __init__(self, crawler):
        super().__init__()
        self.crawler = crawler

    re_type_html = re.compile(r'(text\/html\;)')

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    self.links = self.links + [newUrl]

    def handle_data(self, data):
        # Strip text that is unusable remove any new line characters (replace with space)
        self.innerText += Excl.stripHtml(data)
        Crawler.animate_work(delay=0)

    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        self.crawler.cprint(steps=[0], url=url)

        with urlopen(url) as response:
            if LinkParser.re_type_html.match(response.getheader('Content-Type')) is not None:
                htmlBytes = response.read()
                self.htmlString = htmlBytes.decode("utf-8")
                self.innerText = ""
                self.crawler.cprint(steps=[1], url=url)
                self.feed(self.htmlString)
                response.close()
                return self.innerText, self.links
            else:
                response.close()
                return "",[]

class Crawler():

    re_valid_url = re.compile(r'\bhttps\:\/\/(www\.){0,1}(en|simple|de|es|bs|da|ms|fi|fr|it|pam|af|frr|nl|ceb|war|eu)\.wikipedia\.org')
    re_is_not_article = re.compile(r'[#?=]|(Wikipedia:)|(\.svg)|(\.jpg)|(\.png)|(\.gif)|(\.mp4)|(\.tiff)|(\.bmp)|(https:/[^\/])|(http:/[^\/])')
    anim_idx = 0
    anim = "/–\\|"
    anim_calls = 0

    def __init__(self, write_html_to='CrawledPages.csv', state_file='Crawler.state', maxPages=10000, resume=False):
        self.pagesVisited = []
        self.write_to = write_html_to
        self.state_file = state_file
        self.pagesToVisit = []
        self.maxPages = maxPages

        try:
            with open(state_file, 'rb') as file:
                state = Crawler.mapState(pickle.load(file), '3')
                if (resume):
                    self.pagesToVisit = state['d']['pages-to-visit']
                file.close()
        except:
            try: # Old standard State file 
                with open('Spider.state', 'rb') as file:
                    state = Crawler.mapState(pickle.load(file), '3')
                    if (resume):
                        self.pagesToVisit = state['d']['pages-to-visit']
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
        
    '''
    Mapping state to different versions
    Mapping down may lead to loss of state variables
    '''
    def mapState(src, targetVersion):
        srcVersion = src['v']
        pagesVisited = []
        pagesToVisit = []

        if (srcVersion is targetVersion):
            return src

        if (srcVersion is '1'):
            pagesVisited = src['d']
        if (srcVersion is '2'):
            pagesVisited = src['d']['pv']
            pagesToVisit = src['d']['tv']
        if (srcVersion is '3'):
            pagesToVisit = src['d']['pages-to-visit']
        
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
        
        return src
        
    '''
    Save state as binary
    '''
    def saveState(self):
        try:
            with open(self.state_file, 'wb') as file:
                pickle.dump({
                    'v': '3',
                    'd': {
                        'pages-to-visit': self.pagesToVisit
                    }
                }, file)
                file.close()
        except:
            print('Could not save state to: ', self.state_file)

    '''
    Creates and animation like {/} > {–} > {\} > {|}
    '''
    def animate_work(force=False, times=1, delay=.1):
        Crawler.anim_calls = (Crawler.anim_calls + 1) % 50
        newAnim = Crawler.anim_calls is 0
        for i in range(times):
            if (newAnim or force):
                if (delay > .09):
                    time.sleep(delay)
                Crawler.anim_idx += 1
            print_string = ' {' + Crawler.anim[Crawler.anim_idx % len(Crawler.anim)] + '}'
            if (newAnim or force):
                print(print_string, end='\r', flush=True)
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
        'State SAVE   ' # 7
    ]

    def cprint(self, steps=None, url=None, error=None, end=None, flush=True, custom=None):
        print('\r', end='\r')
        print_string = ''
        if (not custom is None):
            print_string = custom
        else:
            if (not error is None):
                print_string = str(error) + ': '
            else:
                print_string = Crawler.animate_work() + ' '
                print_string += str(len(self.pagesVisited) + 1).rjust(5) + ' - '

        if (not steps is None):
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

        print(print_string, end=end or '\r', flush=flush)

        return print_string
        

    '''
    Start crawling wikipedia. Exit with CTRL+C (for Linux and Windows).
    '''
    def crawl(self, maxPages=None, write_html_to=None):
        if (write_html_to is None):
            write_html_to = self.write_to
        if (maxPages is None):
            maxPages = self.maxPages
        
        csvAppender = CsvAppender(write_html_to)
        do_save_state = 0
        initial = True

        # The main loop. Create a LinkParser and get all the links on the page.
        try:
            while len(self.pagesVisited) < self.maxPages and self.pagesToVisit != []:
                # Start from the beginning of our collection of pages to visit:
                url = self.pagesToVisit[0]
                self.pagesToVisit = self.pagesToVisit[1:]
                
                do_save_state = (do_save_state + 1) % 50
                if (do_save_state == 0):
                    self.saveState()

                if (not url in self.pagesVisited or initial):
                    # self.cprint(steps=[1], url=url)
                    parser = LinkParser(self)

                    try:
                        innerText, links = parser.getLinks(url)
                    except error.HTTPError as he:
                        self.cprint(error=he, url=url, end='\n')
                        continue
                    except error.URLError as urle:
                        self.cprint(error=urle, url=url, end='\n')
                        continue
                    except UnicodeEncodeError as uee:
                        self.cprint(error=uee, url=url, end='\n')
                        continue

                    self.cprint(steps=[2], url=url)
                    links = list([l for l in links if (not l in self.pagesVisited) and Crawler.re_valid_url.match(l) is not None and Crawler.re_is_not_article.search(l) is None])
                    Crawler.animate_work(True)
                    # append html to file
                    if (not url is None and not url in self.pagesVisited):
                        self.cprint(steps=[3], url=url)
                        appended = csvAppender.append(url, innerText)
                        if appended:
                            self.cprint(steps=[4], url=url)
                            initial = False
                        else:
                            self.cprint(steps=[5], url=url, end='\n')
                    else:
                        self.cprint(steps=[5], url=url, end='\n')

                    Crawler.animate_work(True)
                    # Add the pages that we should visit next to the end of our collection
                    # of pages to visit:
                    random.shuffle(links)
                    Crawler.animate_work(True)
                    weight = 3
                    lang = CsvAppender.getLang(url)
                    if (lang is 'G' or lang is 'E'):
                        weight = 4
                    links = links[:weight]
                    self.pagesToVisit = self.pagesToVisit + links
                    Crawler.animate_work(True)
                    random.shuffle(self.pagesToVisit)
                    self.pagesToVisit = self.pagesToVisit[:200]
                    self.pagesVisited.append(url)
        
        except KeyboardInterrupt as ki:
            self.cprint(error='KeyboardInterrupt', steps=[6, 7], end='\n')
            self.saveState()




crawler = Crawler(resume=True, write_html_to='Random_Wiki_Pages.csv')
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

