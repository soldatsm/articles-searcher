# TODO Скрипт для поиска статей по их названию
# TODO Думаю что он будет работать через Bio и eutils
# TODO Либо тупо через гугл поиск, обычно первая ссылка на пабмед всегда
# TODO Добавить итеграцию с селениумом
#

import argparse
from tqdm import tqdm
import requests as re
import json

parser = argparse.ArgumentParser()

parser.add_argument('input')
parser.add_argument('output')
parser.add_argument('-data_type', help='if data is in formated like only names titles -- 0'
                                       'like  oneline -- 1, raw -- 2', choices=[0, 1, 2], type=int)

args = parser.parse_args()


def reader_raw(path):
    with open(fr'{path}') as read_file:
        data = read_file.read().split('\n\n')

    data = [i.split(').')[1].strip().replace('\n', ' ') for i in data]
    data = [i.split('.')[0].split('?')[0] for i in data]
    names = ['%20'.join(i.split()) for i in data]
    return names


def reader_oneline(path):
    with open(fr'{path}') as read_file:
        data = read_file.readlines()
    data = [i.split(').')[1].strip().replace('\n', ' ') for i in data]
    data = [i.split('.')[0].split('?')[0] for i in data]
    names = ['%20'.join(i.split()) for i in data]
    return names


def reader_titles(path):
    with open(fr'{path}') as read_file:
        data = read_file.readlines()
    names = ['%20'.join(i.split()) for i in data]
    return names


def searcher(url):
    handelr = re.get(url)
    json_data = json.loads(handelr.text)
    pmid = json_data['esearchresult']['idlist']
    handelr.close()
    return pmid


def doi_extractor(s_id):
    s_doi = ''
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={s_id}&retmode=text&rettype=abstarts'

    mini_handler = re.get(url)
    handle = mini_handler.text
    mini_handler.close()

    for i in handle.split('\n'):
        if 'DOI' in i:
            s_doi = i.split(':')[1].strip()
    return s_doi


if __name__ == '__main__':

    ids = []
    DOI_list = []

    names = reader_raw(args.input)

    urls = [
        f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?\
        db=pubmed&retmode=json&retmax=1000&field=title&term={name}'
        for name in names
        ]

    for url in tqdm(urls, desc='searching for ids'):
        ids.append(searcher(url))

    for id_i in ids:
        DOI_list.append(doi_extractor(id_i))

    for id_i, doi_j in zip(ids, DOI_list):
        with open(fr'{args.output}', 'a') as write_file:
            write_file.writelines(f'{str(id_i)}--{str(doi_j)}\n')

    print(ids)
    print(DOI_list)
