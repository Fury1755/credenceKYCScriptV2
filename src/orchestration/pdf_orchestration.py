"""This module orchestrates KAH extraction from pdf files."""

from boundary import pdf_io
from core import pdf_processing
from playwright.sync_api import Page


def get_individuals(page: Page, site_url: str, pdf_item: dict[str, str]):
    """Returns a list of Individuals"""
    pdf = pdf_io.download_pdf(page, site_url, pdf_item)
    individual_list = pdf_processing.process_pdf(pdf)
    return individual_list
