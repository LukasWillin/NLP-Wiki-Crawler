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
    re_rem = re.compile(r'[^a-zA-ZäÄöÖüÜëËïÏåÅáÁàÀąĄóÓòÒøØèÈéÉêÊęĘćĆčČùâúÚÙÂôÔĩĨìÌíÍńŃǹǸñÑłŁƚȽżŻšŠśŚ\ ]')
    re_space = re.compile(r'[\t\n\r\.\:\;\,\-\_\"\'\?\!\(\)\{\}\*\@\+\-\<\>\/\\\|0-9]')
    re_whitespace_trim = re.compile(r'(\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ |\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ |\ \ \ \ \ \ \ \ \ \ |\ \ \ \ \ \ \ \ |\ \ \ \ \ \ |\ \ \ \ |\ \ |\t)')
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

    def stripHtml(html):
        Spider.animate_work(True)
        html = Excl.re_space.sub(' ', html)
        Spider.animate_work(True)
        html = Excl.re_rem.sub('', html)
        Spider.animate_work(True)
        return Excl.re_exclude.sub('', html) # Excl.re_whitespace_trim.sub(' ', Excl.re_whitespace_trim.sub(' ', Excl.re_whitespace_trim.sub(' ', Excl.re_exclude.sub('', Excl.re_rem.sub('', Excl.re_space.sub(' ', html))))))

Excl.add_to_exclusion_list(r'autocollapse statecollapsed wikipedia Wikipedia wpsearch QUERY TERMS ShortSearch document documentElement className  document documentElement className replace      s client nojs  s       client js         window RLQwindow RLQ    push function   mw config set   wgCanonicalNamespace      wgCanonicalSpecialPageName  false  wgNamespaceNumber     wgPageName   P value   wgTitle   P value   wgCurRevisionId             wgRevisionId             wgArticleId          wgIsArticle  true  wgIsRedirect  false  wgAction   view   wgUserName  null  wgUserGroups       wgCategories ')
Excl.add_to_exclusion_list(r'editWarning wgStructuredChangeFilters  mediawiki action edit collapsibleFooter href  site   mediawiki page startup   mediawiki page ready   mediawiki searchSuggest   ext charinsert   ext gadget teahouse   ext gadget ReferenceTooltips   ext gadget watchlist notice   ext gadget DRN wizard   ext gadget charinsert   ext gadget refToolbar   ext gadget extra toolbar buttons   ext gadget switcher   ext centralauth centralautologin   ext CodeMirror   mmv head   mmv bootstrap autostart   ext popups   ext visualEditor desktopArticleTarget init   ext visualEditor targetLoader   ext eventLogging   ext wikimediaEvents   ext navigationTiming   ext uls compactlinks   ext uls interface   ext quicksurveys init   ext centralNotice geoIP   skins vector js  mw loader load RLPAGEMODULES')
Excl.add_to_exclusion_list(r'mw config set wgInternalRedirectTargetUrl  wgCanonicalNamespace wgRedirectedFrom Sitenotice title Hjlp sitenotice UTC  wgCanonicalSpecialPageName  false  wgNamespaceNumber     wgPageName   P value   wgTitle   P value   wgCurRevisionId             wgRevisionId             wgArticleId          wgIsArticle  true  wgIsRedirect  false  wgAction   view   wgUserName  null  wgUserGroups       wgCategories   Articles with short description')
Excl.add_to_exclusion_list(r'wgRelevantPageName wgBackendResponseTime wgHostname wgRelevantArticleId wgSiteNoticeId dismissableSiteNotice cqd ng required helpers helplink htmlform ooui htmlform DateInputWidget userSuggest htmlform htmlform ooui UserInputWidget DateInputWidget thanks corethank   wgRequestId  XNmm QpAIEIAAA SGIAAABD  wgCSPNonce  wgIsProbablyEditable  wgRelevantPageIsProbablyEditable  wgRestrictionEdit  wgRestrictionMove  wgMediaViewerOnClick  wgMediaViewerEnabledByDefault  wgPopupsReferencePreviews  wgPopupsConflictsWithNavPopupGadget  wgVisualEditor  pageLanguageCode  en  pageLanguageDir  ltr  pageVariantFallbacks  en  wgMFDisplayWikibaseDescriptions  search  nearby    tagline   wgRelatedArticles  wgRelatedArticlesUseCirrusSearch  wgRelatedArticlesOnlyUseCirrusSearch  wgWMESchemaEditAttemptStepOversample  wgPoweredByHHVM  wgULSCurrentAutonym  English  wgNoticeProject   wgCentralNoticeCookiesToDelete  wgCentralNoticeCategoriesUsingLegacy  Fundraising  fundraising  wgWikibaseItemId  Q     wgCentralAuthMobileDomain  wgEditSubmitButtonLabelPublish    state   styles    globalCssJs user styles    globalCssJs styles    styles   noscript   user styles    globalCssJs user    globalCssJs    user   user options   user tokens  loading  cite styles    math styles    legacy shared    legacy commonPrint    toc styles   wikibase      noscript    interlanguage    wikimediaBadges    d styles    skinning     styles     implement user tokens tffind  jQuery require module  displaystyle X displaystyle  alpha Leftrightarrow wgPageParseReport limitreport cputime  walltime  ppvisitednodes  limit  ppgeneratednodes  limit  postexpandincludesize  limit  templateargumentsize limit  expansiondepth  limit  expensivefunctioncount  limit unstrip depth  limit  unstrip size  limit  entityaccesscount  limit timingprofile   Templat References    total   Templat Cite journal   Templat Main other scribunto limitreport timeusage   limit   limitreport memusage   limit  cachereport origin timestamp  ttl  transientcontent      context  https  schema  type  Article  name  Nilai url  https  wiki Nilai sameAs  http  www wikidata  entity  mainEntity  nomin  user tokens  editToken     patrolToken     watchToken     csrfToken        cite ux enhancements  math scripts         toc')
Excl.add_to_exclusion_list(r'parser output tmulti thumbinner display flex flex direction column autoconfirmed sysop wgCoordinates parser output tmulti trow display flex flex direction row clear left flex wrap wrap width  box sizing border box  parser output tmulti tsingle margin px float left  parser output tmulti theader clear both font weight bold text align center align self center background color transparent width  parser output tmulti thumbcaption text align left background color transparent  parser output tmulti text align left text align left  parser output tmulti text align right text align right  parser output tmulti text align center text align center all and max width px parser output tmulti thumbinner width  important box sizing border box max width none important align items center  parser output tmulti trow justify content center  parser output tmulti tsingle float none important max width  important box sizing border box text align center  parser output tmulti thumbcaption text align center')
Excl.add_to_exclusion_list(r'wgBreakFrames wgMonthNamesShort XNjswwpAIEIAAIU iM AAACN LCCN identifiers articles VIAF identifiers articles WorldCat VIAF identifiers   wgFlaggedRevsParams tags accuracy levels  quality  pristine wgStableRevisionId    de  de     Deutsch                   flaggedRevs basic   wzrrbt   variant  de          editMenus  WikiMiniAtlas  OpenStreetMap  CommonsDirekt       startUp flaggedRevs advanced   Collider Detector at Fermilab   XNnpDgpAMFQAAJ dO wAAAAK    wgFlaggedRevsParams tags accuracy levels  quality  pristine wgStableRevisionId    de  de     Deutsch                     flaggedRevs basic   wzrrbt   variant  de            editMenus  WikiMiniAtlas  OpenStreetMap  CommonsDirekt      startUp flaggedRevs advanced var nodedocument getElementById  dismissablenotice anonplace  if node node outerHTML u  Cdiv class  dismissable u  E u  Cdiv class  dismissable close  u  E u  Ca tabindex role button  u  Ezarrar u  C a u  E u  C div u  E u  Cdiv class  dismissable body  u  E u  Cdiv id localNotice  lang ast  dir  u  E u  Ctable style  class noprint plainlinks ambox ambox u  E n u  Ctbody u  E u  Ctr u  E n u  Ctd class ambox image  u  E n u  Cdiv style  u  E u  Cimg alt  src upload wikimedia org commons thumb a ac Noun Project maintenance icon cc svg Noun Project maintenance icon cc svg png  decoding async height  srcset upload wikimedia org commons thumb a ac Noun Project maintenance icon cc svg Noun Project maintenance icon cc svg png x wgPageContentLanguage  de  wgPageContentModel  wikitext  wgSeparatorTransformTable  t t wgDigitTransformTable  wgDefaultDateFormat  dmy  wgMonthNames')
Excl.add_to_exclusion_list(r'templates January  wgRelevantUserName bibcoded see bibcode Bibcode February March April May June July August September October November December Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Template User Talk Pages XNmiKwpAMFoAAHP gAAABG Template User Talk Pages From the free encyclopedia Jump to navigation Jump to v e User Talk Pages User talk pages Usertalkpage User talk Usertalkback Userwhisperback Talk header preload Message Talkpagecool User notification preference Notification preferences NP Usertalkpage rounded User talk rules User talk top Usercomment Usertalkconcise Talk header User talk header Usertalksuper Usertalkpage blue User mbox Category Template documentation Initial visibility currently defaults to autocollapse To this template initial visibility the parameter may be used statecollapsed User Talk Pages')
Excl.add_to_exclusion_list(r'Template Multiple issues Template Template Multiple issues Multiple issues template protected templates using small message boxes Exclude in print message templates message templates missing parameters Templates used by Twinkle Templates used by AutoWikiBrowser Lua based templates Templates using TemplateData templates Templates that add tracking category January February March April May June July August September October November December Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Template Multiple issues XNnEWApAIC AAKhyJIkAAAAA templateeditor templateeditor templateData templateData images inputBox ui input ui checkbox oojs ui core oojs ui indicators oojs ui textures widgets oojs ui icons oojs ui icons alerts oojs ui icons interactions jquery makeCollapsible ui jquery tablesorter jquery makeCollapsible Template Multiple issues From the free encyclopedia Jump to navigation Jump to This article has multiple issues Please help improve it or discuss')
Excl.add_to_exclusion_list(r'shortcutboxplain solid aaa fff em padding em em em em shortcutlist inline block bottom solid aaa bottom em normal shortcutanchordiv position relative top em Shortcuts WP REFB WP REFBEGIN WP REFSTAR')
# An appender which strips the html from unnecessary content
# Appends the text to a csv for storage
class CsvAppender:
    re_en = re.compile(r'((\bhttps\:\/\/)(www\.){0,1}(en|simple)\.wikipedia\.org)')
    re_de = re.compile(r'((\bhttps\:\/\/)(www\.){0,1}de\.wikipedia\.org)')
    re_x = re.compile(r'(\bhttps\:\/\/|\b)(www\.){0,1}((es|bs|da|ms|fi|fr|it|pam|af|frr|nl|ceb|war|eu)\.wikipedia\.org)')

    def __init__(self, target_file):
        self.target_file = target_file

    def getLang(url):
        lang = None
        if (CsvAppender.re_de.search(url) is not None):
            lang = 'G'
        elif (CsvAppender.re_en.search(url) is not None):
            lang = 'E'
        elif (CsvAppender.re_x.search(url) is not None):
            lang = 'X'
        
        return lang

    def append(self, url, html):
        lang = CsvAppender.getLang(url)

        if (lang is None):
            return False

        html = ' '.join(Excl.stripHtml(html)[:6000].split())
        Spider.animate_work(True)

        with Path(self.target_file) as file_p:
            if (not file_p.exists()):
                with open(self.target_file, 'w', encoding='utf-8') as file_w:
                    file_w.write('language;url;text\n')
                    file_w.close()
        
        with open(self.target_file, 'a', encoding='utf-8') as file:
            file.write(lang + ';' + url + ';' + html[:4000] + '\n')
            file.close()

        # Strip text that is unusable remove any new line characters (replace with space)
        # Then store the text at the end of the existing file or create it
        return True

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):

    re_type_html = re.compile(r'(text\/html\;)')

    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag.lower() == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]

    def handle_data(self, data):
        self.innerText += data + ' '
        Spider.animate_work()

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
        with urlopen(url) as response:
            # Make sure that we are looking at HTML and not other things that
            # are floating around on the internet (such as
            # JavaScript files, CSS, or .PDFs for example)
            # print(response.getheader('Content-Type'))
            if LinkParser.re_type_html.match(response.getheader('Content-Type')) is not None:
                htmlBytes = response.read()
                # Note that feed() handles Strings well, but not bytes
                # (A change from Python 2.x to Python 3.x)
                self.htmlString = htmlBytes.decode("utf-8")
                self.innerText = ""
                self.feed(self.htmlString)
                response.close()
                return self.innerText, self.links
            else:
                response.close()
                return "",[]

# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
class Spider():

    re_valid_url = re.compile(r'(https\:\/\/|\b)(www\.){0,1}((en|de|es|bs|da|simple|ms|fi|fr|it|pam|af|frr|nl|ceb|war|eu)\.wikipedia\.org)')
    re_is_not_article = re.compile(r'[#?=]|(Wikipedia:)|(\.svg)|(\.jpg)|(\.png)|(\.gif)|(\.mp4)|(\.tiff)|(\.bmp)|(https:/[^\/])|(http:/[^\/])')
    anim_idx = 0
    anim = "/–\\|"
    anim_calls = 0

    def __init__(self, write_html_to='SpiderPig.csv', state_file='Spider.state', maxPages=10000, resume=False):
        self.pagesVisited = []
        self.write_to = write_html_to
        self.state_file = state_file
        self.pagesToVisit = []
        self.maxPages = maxPages

        try:
            with open(state_file, 'rb') as file:
                state = pickle.load(file)
                state = Spider.mapState(state, '2')
                self.pagesVisited = state['d']['pv']
                if (resume):
                    self.pagesToVisit = state['d']['tv']
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
        
        return src
        

    def saveState(self):
        try:
            with open(self.state_file, 'wb') as file:
                pickle.dump({
                    'v': '2',
                    'd': {
                        'pv': self.pagesVisited,
                        'tv': self.pagesToVisit
                    }
                }, file)
                file.close()
        except:
            print('Could not save state to: ', self.state_file)

    def animate_work(force=False, times=1):
        Spider.anim_calls = (Spider.anim_calls + 1) % 500
        newAnim = Spider.anim_calls is 0
        for i in range(times):
            if (newAnim or force):
                time.sleep(.14)
                Spider.anim_idx += 1
            print_string = ' {' + Spider.anim[Spider.anim_idx % len(Spider.anim)] + '}'
            if (newAnim or force):
                print(print_string, end='\r', flush=True)
        return print_string

    def appendUrl(self, url):
        self.pagesToVisit.append(url)

    def crawl(self, maxPages=None, write_html_to=None):
        if (write_html_to is None):
            write_html_to = self.write_to
        if (maxPages is None):
            maxPages = self.maxPages
        
        csvAppender = CsvAppender(write_html_to)
        do_save_state = 0
        initial = True
        kb_interrupt = False
        # The main loop. Create a LinkParser and get all the links on the page.
        # Also search the page for the word or string
        # In our getLinks function we return the web page
        # (this is useful for searching for the word)
        # and we return a set of links from that web page
        # (this is useful for where to go next)
        while len(self.pagesVisited) < self.maxPages and self.pagesToVisit != [] and not kb_interrupt:
            # Start from the beginning of our collection of pages to visit:
            url = self.pagesToVisit[0]
            self.pagesToVisit = self.pagesToVisit[1:]
            do_save_state = (do_save_state + 1) % 50
            Spider.animate_work(True)
            print_string = ''
            cols, lines = shutil.get_terminal_size(fallback=(80, 24))
            if (do_save_state == 0):
                self.saveState()
            if (not url in self.pagesVisited or initial or not kb_interrupt):
                try:
                    print_string += " " + str(len(self.pagesVisited)) + ' Visiting: ' + url
                    if len(Spider.animate_work() + print_string) + 22 >= cols:
                        print_string = print_string[:cols-22 + len(Spider.animate_work())]
                    print((Spider.animate_work() + print_string + ' ** Page PARSING ** ').ljust(cols), end='\r', flush=True)
                    parser = LinkParser()
                    Spider.animate_work(True)
                    innerText, links = parser.getLinks(url)
                    print((Spider.animate_work() + print_string + ' ** Links FILTER ** ').ljust(cols), end='\r', flush=True)
                    links = list([l for l in links if (not l in self.pagesVisited) and Spider.re_valid_url.search(l) is not None and Spider.re_is_not_article.search(l) is None])
                    Spider.animate_work(True, 3)
                    # append html to file
                    if (not initial and not url in self.pagesVisited and not url is None):
                        print((Spider.animate_work() + print_string + ' ** Page SAVING  ** ').ljust(cols), end='\r', flush=True)
                        appended = csvAppender.append(url, innerText)
                        if appended:
                            print_string += " ** Page SAVE OK ** "
                            initial = False
                        else:
                            print_string += " ** Page IGNORED ** "
                    else:
                        print_string += " ** Page IGNORED ** "
                        initial = False

                    print_string = print_string.ljust(cols-1)[:cols - len(Spider.animate_work())]
                    print(Spider.animate_work() + print_string, end='\r', flush=True)
                    Spider.animate_work(True, 3)
                    # Add the pages that we should visit next to the end of our collection
                    # of pages to visit:
                    random.shuffle(links)
                    weight = 2
                    lang = CsvAppender.getLang(url)
                    if (lang is 'G' or lang is 'E'):
                        weight = 3
                    links = links[:weight]
                    self.pagesToVisit = self.pagesToVisit + links
                    random.shuffle(self.pagesToVisit)
                    self.pagesToVisit = self.pagesToVisit[:100]
                    self.pagesVisited.append(url)
                except error.HTTPError as e:
                    e_string = str(e)
                    len_e_string = len(e_string)
                    len_visit_string = len(str(len(self.pagesVisited)) + ' Visiting:')
                    len_e_string -= len_visit_string
                    if (len_e_string < 0):
                        len_e_string = 0
                    print_string = " " + e_string + print_string[len_visit_string:(cols-len_e_string)] + '\n'
                except error.URLError as urle:
                    e_string = str(urle)
                    len_e_string = len(e_string)
                    len_visit_string = len(str(len(self.pagesVisited)) + ' Visiting:')
                    len_e_string -= len_visit_string
                    if (len_e_string < 0):
                        len_e_string = 0
                    print_string = " " + e_string + print_string[len_visit_string:(cols-len_e_string)] + '\n'
                except UnicodeEncodeError as ue:
                    e_string = str(ue)
                    len_e_string = len(e_string)
                    len_visit_string = len(str(len(self.pagesVisited)) + ' Visiting:')
                    len_e_string -= len_visit_string
                    if (len_e_string < 0):
                        len_e_string = 0
                    print_string = " " + e_string + print_string[len_visit_string:(cols-len_e_string)] + '\n'
                except KeyboardInterrupt as ki:
                    print_string = ('\n' + str(ki) + ' > Stop crawling & save state\n').ljust(cols)[:cols]
                    kb_interrupt = True
                    self.saveState()
            print(Spider.animate_work() + print_string, end="\r", flush=True)
            

    

spider = Spider(resume=True, write_html_to='Random_Wiki_Pages.csv')
spider.appendUrl('https://simple.wikipedia.org/wiki/Main_Page')
spider.appendUrl('https://de.wikipedia.org/wiki/Wikipedia:Hauptseite')
spider.appendUrl('https://da.wikipedia.org/wiki/Forside')
spider.appendUrl('https://es.wikipedia.org/wiki/Wikipedia:Portada')
spider.appendUrl('https://bs.wikipedia.org/wiki/Po%C4%8Detna_strana')
spider.appendUrl('https://frr.wikipedia.org/wiki/National_Diet_Library')
spider.appendUrl('https://af.wikipedia.org/wiki/Tuisblad')
spider.appendUrl('https://pam.wikipedia.org/wiki/Luna,_Apayao')
spider.appendUrl('https://eu.wikipedia.org/wiki/Lucio_Marineo_S%C3%ADculo')
spider.appendUrl('https://war.wikipedia.org/wiki/Andrena_flavofacies')
spider.appendUrl('https://ceb.wikipedia.org/wiki/Aoso_Yama')
spider.appendUrl('https://sv.wikipedia.org/wiki/L%C3%A5ngserieb%C3%B6cker')
spider.appendUrl('https://nl.wikipedia.org/wiki/Giovanni_Battista_Piranesi')
spider.appendUrl('https://it.wikipedia.org/wiki/Pagina_principale')
spider.appendUrl('https://ms.wikipedia.org/wiki/Laman_Utama')
spider.appendUrl('https://fr.wikipedia.org/wiki/William_Gallacher')
spider.crawl()

