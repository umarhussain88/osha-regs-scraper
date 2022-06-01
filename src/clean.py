from urllib import response
import pandas as pd
from bs4 import BeautifulSoup
from dataclasses import dataclass
from io import BytesIO


@dataclass
class Clean:

    # this might need to be a stream? or azure blob storage?

    def create_csv_dataframe_from_stream(self, stream: bytes) -> pd.DataFrame:

        df = pd.read_csv(BytesIO(stream))

        return df

    def standards_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe["Name"] = dataframe["standard_title"].str.extract(
            "Part (\d+) -")
        dataframe["Content"] = (
            dataframe["standard_page_title"] +
            "\n" + dataframe["standard_content"]
        )
        final_df = dataframe[["Name", "Content"]]

        return final_df

    def create_bs4_object_from_series(self, df: pd.Series) -> BeautifulSoup:

        df = df.apply(lambda x: BeautifulSoup(x, "html.parser"))
        return df

    def get_article_from_html(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        articles = dataframe["article"].apply(
            lambda x: BeautifulSoup(x, "html.parser"))
        dataframe["ExternalId"] = articles.apply(
            lambda x: x.find("article").get("data-history-node-id")
        )

        dataframe = dataframe.rename(columns={"article": "content"})
        return dataframe

    # strip title column
    def strip_title(self, df: pd.DataFrame):

        df1 = df.copy()
        df1["title"] = df1["title"].str.split("- \[\d", expand=True)[0]
        df1["title"] = df1["title"].str.strip()  # remove whitespace
        df1["content"] = df1["content"] + df1["article_title"]

        df1 = df1.drop("article_title", axis=1)

        return df1

    # create citation dataframe
    def citation_df(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Explodes along the title column after splitting out citations.
        joins and uses externalId for many:1 join"""

        citation_df = (
            dataframe[["ExternalId"]]
            .join(
                dataframe["title"]
                .str.split("- \[", expand=True)[1]
                .str.replace("\[|\]", "", regex=True)
                .str.split(";")
                .explode()
            )
            .reset_index(drop=True)
        )

        return citation_df.rename(columns={1: "Content"})

    def remove_ul_header(self, soup: pd.Series) -> BeautifulSoup:

        for node in soup.findAll("ul", {"class": "bulleted-list-header node-header"}):
            node.decompose()

        return soup.prettify()

    def remove_copyright_header(self, soup: pd.Series) -> BeautifulSoup:

        for node in soup.findAll("section", {"class": "block clearfix"}):
            node.decompose()

        return soup.prettify()

    def parse_reponse_text_html(self, dataframe: pd.DataFrame) -> pd.Series:
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

    def parse_regulations(self, dataframe: pd.DataFrame) -> pd.Series:
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
