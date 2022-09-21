from text_utils.korean import normalize
from tqdm.auto import tqdm
import argparse
import random
import nltk
import json
import os
import re
nltk.download('punkt')


def cleaner(text:str, min_len:int, max_len:int):
    text = re.sub('[\w\.-]+@[\w\.-]+', '', text)
    text = re.sub('\([^)]*\)', '', text) # 소괄호 포함 소괄호 내부 문자 제거
    text = re.sub('\[[^)]*\]', '', text) # 대괄호 포함 대괄호 내부 문자 제거
    text = re.sub('[가-힣]+ 기자', '', text) # 특정 패턴 제거
    text = re.sub('재판매 및 DB 금지', '', text) # 특정 문구 제거
    text = normalize(text) # text normalizing
    text = re.sub('[(\n)]', '', text) # 다중 개행문자 제거
    text = re.sub('[(\.)]', '.\n', text) # 마침표 기준 개행문자 추가
    text = re.sub('[^ \n~?!.,ㄱ-ㅣ가-힣+]', '', text) # 한글만 출력
    text = re.sub(' +', ' ', text) # 다중 공백 하나로 축소
    text = [t.strip() for t in text.split('\n') if len(t) > min_len and len(t) < max_len] # 개행문자 기준으로 split
    return text


def processor(args):
    lines = []
    assert os.path.isfile(args.metadata_path)
    with open(args.metadata_path, 'r', encoding='utf8') as j:
        metadata = json.loads(j.read())
        for num in tqdm(metadata.keys()):
            info = metadata[str(num)]
            for key, value in info.items():
                if key == 'elements':
                    try:
                        sub_lines = cleaner(value, min_len=args.min_len, max_len=args.max_len)
                        lines += sub_lines
                    except Exception as e:
                        print(e)
                        
    lines = list(set(lines))
    random.shuffle(lines)
    lines = '\n'.join(lines)
    os.makedirs(args.output_directory, exist_ok=True)
    output_path = os.path.join(args.output_directory, args.output_file_name)
    
    with open(output_path, 'w', encoding='utf8') as f:
        f.write(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--metadata_path', type=str, required=True)
    parser.add_argument('--min_len', type=int, default=5)
    parser.add_argument('--max_len', type=int, default=190)
    parser.add_argument('--output_directory', type=str, default='data')
    parser.add_argument('--output_file_name', type=str, default='script.txt')
    args = parser.parse_args()
    processor(args)
    
if __name__ == "__main__":
    main()