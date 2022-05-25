from urllib import response
import pandas as pd
from bs4 import BeautifulSoup


def parse_reponse_text_html(dataframe: pd.DataFrame) -> pd.Series:
    """Removes the unecessary HTML tags and returns the letter as parsed HTML

    Args:
        dataframe (pd.DataFrame): the dataframe containing the HTML text

    Returns:
        pd.Series: the dataframe with the HTML text parsed as a bs4 object
    """

    response_text_html = dataframe['response_text'].str.replace(
        '\n', '').str.extract('(<b>Response text:</b>.*?</td>)')

    response_text_html = response_text_html.fillna(
        dataframe['response_text'].str.replace(
            '\n', '').str.extract('(<b>Request text:</b>.*?</td>)')

    )

    response_text_html = '<section id="content-wall">' + \
        response_text_html + '</section>'

    # response_text_html = response_text_html.apply(
    #     lambda x: BeautifulSoup(x, 'html.parser'))

    return response_text_html


def parse_regulations(dataframe: pd.DataFrame) -> pd.Series:
    """parses the regulations from a html letter

    the regulations can be in the following format

    <p>178.001, 195.001</p>

    Or it's possible to come in the following format:

    <div>178.001(a);, 195.001(a) & 112.001(c)</div>

    so a generic regex is used to extract the regs and then strip the remaining HTML tags


    Args:
        dataframe (pd.DataFrame): dataframe containing the html response_text

    Returns:
        pd.Series: column with the parsed regulations
    """

    parsed_regs = dataframe['response_text'].str.extract(
        '>(\d+\.\d+.*)</')[0].str.replace(r'<[^<>]*>', '', regex=True)

    return parsed_regs
