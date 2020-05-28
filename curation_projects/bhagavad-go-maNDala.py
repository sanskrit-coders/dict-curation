import codecs
import logging
import os
from functools import partial
from multiprocessing import Pool

import regex
import tqdm
from indic_transliteration import sanscript
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.select import Select

from curation_utils import scraping
from dict_curation import babylon

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s:%(module)s:%(lineno)d %(message)s")



letters = "અ આ ઇ ઈ ઉ ઊ ઋ ઌ ઍ એ ઐ ઑ ઓ ઔ ક ખ ગ ઘ ઙ ચ છ જ ઝ ઞ ટ ઠ ડ ઢ ણ ત થ દ ધ ન પ ફ બ ભ મ ય ર લ ળ વ શ ષ સ હ ૐ ૠ ૡ".split()



def get_letter_headwords(letter, out_path_dir):
    browser = scraping.get_selenium_browser(headless=True)
    out_path = os.path.join(out_path_dir, letter + ".csv")
    if os.path.exists(out_path):
        logging.warning("Skipping %s as %s exists", letter, out_path)
        return 0 
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with codecs.open(out_path, "w", 'utf-8') as file_out:
        url = "http://www.bhagwadgomandal.com/index.php?action=dictionary&sitem=%s&type=1&page=0" % letter
        logging.info("Processing %s", letter)
        browser.get(url=url)
        page_dropdown = None
        num_pages = 1
        try:
            page_dropdown = browser.find_element_by_name("pgInd")
            num_pages = len(page_dropdown.find_elements_by_css_selector("option"))
        except NoSuchElementException:
            logging.warning("Got no pages for %s", letter)
        logging.info("Number of pages: %d for %s", num_pages, letter)
        browser.implicitly_wait(250)
    
        word_count = 0 
        for option_index in range(0, num_pages):
            if page_dropdown is not None:
                Select(page_dropdown).select_by_index(option_index)
                page_dropdown = browser.find_element_by_name("pgInd")
            if word_count % 10 == 0:
                logging.info("Page %s, index %d", letter, option_index)
            word_elements = browser.find_elements_by_css_selector("a.word")
            words = [w.text for w in word_elements]
            word_count = word_count + len(words)
            file_out.write("\n".join(words) + "\n")
            
        browser.close()
        return word_count


def get_headwords(out_path):
    pool = Pool(4)
    f = partial(get_letter_headwords, out_path_dir=out_path)
    counts = pool.map(f, letters)
    logging.info(list(zip(letters, counts)))


def get_definition(headword, browser, existing_definitions={}):
    if headword in existing_definitions and existing_definitions[headword] != "":
        return existing_definitions[headword]
    url = "http://www.bhagavadgomandal.com/index.php?action=dictionary&sitem=%s&type=3&page=0" % headword
    try:
        browser.get(url=url)
    except TimeoutException:
        logging.error("Timed out getting URL %s", url)
        raise 
    for detail_link in browser.find_elements_by_css_selector("a.detaillink"):
        detail_link.click()
    rows = browser.find_elements_by_css_selector("div.right_middle table table tr")
    definition = "%s<br>" % headword
    for row in rows[1:]:
        column_data = [c.text for c in row.find_elements_by_css_selector("td")]
        definition_detail = column_data[3].replace(".", "॥")
        definition_detail = regex.sub("\n+", "<br>", definition_detail)
        row_definition = "%s<br>%s<br><br>" % (" ".join(column_data[0:2]), definition_detail)
        definition = definition + row_definition
    return definition.replace(":", "ઃ")


def dump_letter_definitions(letter, in_path_dir, out_path_dir, out_path_dir_devanagari):
    in_path = os.path.join(in_path_dir, letter + ".csv")
    out_path = os.path.join(out_path_dir, letter + ".babylon")
    out_path_devanagari_entries = os.path.join(out_path_dir_devanagari, letter + ".babylon")
    browser = scraping.get_selenium_browser(headless=True)
    if os.path.exists(out_path) and os.path.exists(out_path_devanagari_entries) :
        logging.warning("Skipping %s since %s exists", letter, out_path)
        return 0
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    os.makedirs(os.path.dirname(out_path_devanagari_entries), exist_ok=True)
    count = 0
    existing_definitions = babylon.get_definitions(out_path)
    with codecs.open(in_path, "r", 'utf-8') as file_in, codecs.open(out_path, "w", 'utf-8') as file_out, codecs.open(out_path_devanagari_entries, "w", 'utf-8') as file_out_devanagari:
        headwords = file_in.readlines()
        progress_bar = tqdm.tqdm(total=len(headwords), desc="Headwords for %s" % letter, position=0)
        log = tqdm.tqdm(total=0, position=3, bar_format='{desc}')
        for headword in headwords:
            headword = headword.strip()
            headword = headword.replace(":", "ઃ")
            definition = get_definition(headword=headword, browser=browser, existing_definitions=existing_definitions)
            devanagari_headword = sanscript.transliterate(data=headword, _from=sanscript.GUJARATI, _to=sanscript.DEVANAGARI)
            devanagari_headword = sanscript.SCHEMES[sanscript.DEVANAGARI].fix_lazy_anusvaara(devanagari_headword)
            definition_devanagari = sanscript.transliterate(data=definition, _from=sanscript.GUJARATI, _to=sanscript.DEVANAGARI)
            devanagari_entry = "%s|%s\n%s\n\n" % (headword, devanagari_headword, definition_devanagari)
            file_out.writelines(["%s|%s\n%s\n\n" % (headword, devanagari_headword, definition.replace("॥", "  ॥ "))])
            file_out_devanagari.writelines([devanagari_entry])
            progress_bar.update(1)
            log.set_description_str(devanagari_entry)
            count = count + 1
    browser.close()
    return count


def dump_definitions(in_path_dir, out_path_dir, out_path_dir_devanagari):
    from tqdm.contrib.concurrent import process_map  # or thread_map
    f = partial(dump_letter_definitions, in_path_dir=in_path_dir, out_path_dir=out_path_dir, out_path_dir_devanagari=out_path_dir_devanagari)
    results = process_map(f, letters, max_workers=8)
    logging.info(list(zip(letters, results)))

def test_get_definition():
    browser = scraping.get_selenium_browser()
    logging.debug(get_definition("અ", browser=browser))
    browser.close()


if __name__ == '__main__':
    # get_headwords(out_path="/home/vvasuki/indic-dict/stardict-gujarati/gu-head/gu-entries/bhagavad-go-maNDala/headwords/")
    # test_get_definition()
    dump_definitions(in_path_dir="/home/vvasuki/indic-dict/stardict-gujarati/gu-head/gu-entries/bhagavad-go-maNDala/headwords/", out_path_dir="/home/vvasuki/indic-dict/stardict-gujarati/gu-head/gu-entries/bhagavad-go-maNDala/mUlam/", out_path_dir_devanagari="/home/vvasuki/indic-dict/stardict-gujarati/gu-head/dev-entries/bhagavad-go-maNDala-dev/mUlam/")
