'''This module handles the searches for individuals.'''
from core.individual import Individual
from playwright.sync_api import Page
from typing import List

def google_search(page: Page, individual: Individual, individual_name: str, screenshots: dict):
    ''' Takes kyc status as input and takes screenshot. Adds result to screenshots.'''
    child = page.context.new_page()
    child.goto(f"https://google.com/search?q={individual_name}")

    while True:
        kyc_ok = input("KYC ok? (Y/N): ")
        if kyc_ok.upper() == "Y" or kyc_ok.upper() == "N":
            individual.kyc_status = True
            screenshots[f"{individual_name} - Google Search"] = child.screenshot()
            individual.google = True
            if kyc_ok.upper() == "N":
                individual.kyc_status = False
            child.close()
            break
        print("Invalid input")


def baidu_search(page: Page, individual: Individual, individual_name: str, screenshots: dict):
    ''' Takes kyc status as input and takes screenshot. Adds result to screenshots.'''
    child = page.context.new_page()
    child.goto(f"https://www.baidu.com/s?wd={individual_name}")

    while True:
        kyc_ok = input("KYC ok? (Y/N): ")
        if kyc_ok.upper() == "Y" or kyc_ok.upper() == "N":
            individual.kyc_status = True
            individual.baidu = True
            screenshots[f"{individual_name}_百度搜索"] = child.screenshot()
            if kyc_ok.upper() == "N":
                individual.kyc_status = False
            break
        print("Invalid input")

    child.close()


def search_for_individual(page: Page, individual: Individual) -> dict[str, dict[str, bytes]]:
    '''This module performs individual Google and Baidu searches,
    and returns a dictionary of screenshots. Mutates individual.kyc_status and
    individual.google, individual.baidu accordingly.'''

    # DbC: Validate individual properties
    if not (individual.name and individual.role):
        raise ValueError("Individual attributes missing")

    while True:
        is_baidu = input(f"Baidu search for {individual.name}? (Y/N):")
        if is_baidu.upper() == "Y":
            break
        if is_baidu.upper() == "N":
            break
        print("Invalid input")

    if is_baidu == "Y":
        individual.baidu = True
        chinese_name = input("Please enter chinese name: ('-' if None)")
        if chinese_name != '-':
            individual.chinese_name = chinese_name

    # perform searches
    # Google first
    screenshots: dict[str, bytes] = {}
    google_search(page, individual, individual.name, screenshots)
    if individual.chinese_name != "-":
        google_search(page, individual, individual.chinese_name, screenshots)
    if individual.baidu is True:
        baidu_search(page, individual, individual.name, screenshots)
        if individual.chinese_name != "-":
            baidu_search(page, individual, individual.chinese_name, screenshots)

    return {f"{individual.name}" : screenshots}

def search_master(page: Page, kah_list: List[Individual]) -> List[dict[str, dict[str, bytes]]]:
    '''The master search function, only called once against a list of individuals.
    Returns a list of dictionaries for each individual.'''
    all_screenshots: List[dict] = []
    for kah in kah_list:
        all_screenshots.append(search_for_individual(page, kah))
    while True:
        has_others = input("Any more entities? (Y/N): ")
        if has_others == "Y":
            new_name = input("Input new entity name: ")
            new_person = Individual(new_name, "-", "-", "-", "-", False, False, False, "RELATED")
            all_screenshots.append(search_for_individual(page, new_person))