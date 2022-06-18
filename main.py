from src import Exporter, logger_util, run_spider, Clean
import os
from sys import argv
from pathlib import Path
import json
import pandas as pd


exp = Exporter(blob_storage_url=os.environ.get('BLOB_STORAGE_URL'),
               blob_container_name=os.environ.get('BLOB_CONTAINER_NAME'))


cl = Clean()

logger = logger_util(__name__)


if __name__ == '__main__':

    if not Path(__file__).parent.joinpath('export').exists():
        Path(__file__).parent.joinpath('export').mkdir()
        logger.info('creating export folder')

    trg_export_path = Path(__file__).parent.joinpath('export')

    if len(argv) != 2:
        print("Usage: python main.py <spider_name> or export-azure")
        logger.error("No spider name provided")
        exit(1)

    if argv[1] == 'export-azure':
        logger.info("Exporting data to Azure Blob Storage")
        for file in trg_export_path.glob('*.csv'):
            df = pd.read_csv(file)
            exp.write_to_blob_storage(file.name, df)

    elif argv[1] == 'create-osha-exports':

        logger.info('Creating OSHA exports')

        # articles.csv  - loi articles
        with open('output/articles.json', 'r') as f:
            j = json.load(f)
            df = pd.json_normalize(j)

        article_df = cl.get_article_from_html(df)
        article_df = cl.strip_title(article_df)
        # very expensive operation - look at doing this in a better way.
        content = cl.create_bs4_object_from_series(article_df["content"])
        content = content.apply(cl.remove_ul_header)
        content = cl.create_bs4_object_from_series(content)
        content = content.apply(cl.remove_copyright_header)
        article_df["content"] = content.copy()
        article_df["created_date"] = pd.Timestamp(
            "now").strftime("%Y-%m-%d %H:%M:%S")

        # citations

        citation_df = cl.citation_df(df)

        # standards dataframe

        with open('output/standards.json', 'r') as f:
            j = json.load(f)
            df = pd.json_normalize(j)

        standards_df = cl.standards_dataframe(df)
        logger.info(f"Dataframe shape: {standards_df.shape}")

        content = cl.create_bs4_object_from_series(standards_df["Content"])

        standards_df['partNumber'] = content.apply(lambda x: x.find(
            'div', {'class': 'views-field views-field-nothing'}).get_text()).str.split('-', expand=True)[0].copy()
        standards_df['partNumber'] = standards_df['partNumber'].str.replace(
            '\(.*\)', '', regex=True).str.replace('[^0-9|\.]', '', regex=True).copy()
        standards_df["created_date"] = pd.Timestamp(
            "now").strftime("%Y-%m-%d %H:%M:%S")

        article_df.to_csv(trg_export_path.joinpath(
            'articles.csv'), index=False)
        standards_df.to_csv(trg_export_path.joinpath(
            'standards.csv'), index=False)
        citation_df.to_csv(trg_export_path.joinpath(
            'citations.csv'), index=False)

    elif argv[1] == 'clean-phmsa-regulations':

        with open('output/phmsa_regulations.json') as f:
            j = json.load(f)

        df = pd.json_normalize(j)

        df['response_text_html'] = cl.parse_reponse_text_html(df)
        df['regulations'] = cl.parse_regulations(df)

        phmsa_regulations = df['regulations'].str.strip().str.replace('&amp;', '').str.replace(
            ',\s', ',', regex=True).str.replace('\s+', ',', regex=True)\
            .str.replace('(,)(\d{1})', r'|\2', regex=True).str.split('|').explode()

        phmsa_citations = df[['ref_id']].join(phmsa_regulations)

        logger.info('saving files')

        df.to_csv(trg_export_path.joinpath(
            'phmsa_regulations.csv'), index=False)

        phmsa_citations.to_csv(trg_export_path.joinpath(
            'phmsa_citations.csv'), index=False)

    else:
        spider_name = argv[1]
        run_spider(argv[1])
