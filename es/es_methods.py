import csv
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')

"""
csv 파일 확인사항  // filename=index (대문자 X) // "," 제거  // 빈칸 채우기  // column 확인 // 지울때는 doc_type 무시가능
인코딩 에러시 euc-kr 또는 utf-8-sig 둘 중 하나 사용
"""

class Data_handler():
    def __init__(self,index, doc_type):
        self.index=index
        self.doc_type=doc_type   #self.__doc_type = 외부에서 변경 불가능

    # 파일 업로드
    def upload_data(self):
        index, doc_type = self.index, self.doc_type
        try:
            f = open('es/data/{0}.csv'.format(index), 'r', encoding='utf-8-sig')  # utf-8 // euc-kr //  encoding='utf-8-sig'
            rdr = csv.reader(f)
            id = 1  # 기존 데이터 업데이트한다면 1  추가할시 기존 id 마지막 다음으로 설정 (346까지 존재)
            for line in rdr:
                try:
                    if schema:          # 첫 행 스키마
                        csv_data = line
                        doc = {}
                        for i in range(len(schema)):
                            if not csv_data[i]:
                                csv_data= " "
                            doc[schema[i]] = csv_data[i]
                        res = es.index(index=index, doc_type=doc_type, id=id, body=doc)
                        #print(id, res)
                        id += 1
                except:
                    schema = line
            f.close()
        except UnicodeDecodeError:
            f = open('es/data/{0}.csv'.format(index), 'r', encoding='euc-kr')  # utf-8 // euc-kr //  encoding='utf-8-sig'
            rdr = csv.reader(f)
            id = 1  # 기존 데이터 업데이트한다면 1  추가할시 기존 id 마지막 다음으로 설정 (346까지 존재)
            for line in rdr:
                try:
                    if schema:  # 첫 행 스키마
                        csv_data = line
                        doc = {}
                        for i in range(len(schema)):
                            if not csv_data[i]:
                                csv_data = " "
                            doc[schema[i]] = csv_data[i]
                        res = es.index(index=index, doc_type=doc_type, id=id, body=doc)
                        #print(id, res)
                        id += 1
                except:
                    schema = line
            f.close()


    def delete_index(self):
        index = self.index
        res = es.indices.delete(index=index, ignore=[400, 404])
        result = list(res.values())
        if result[0] == True:
            print("The index has been deleted")
        else:
            print("Failed to delete the index")

    # size 검색되는 건수
    def search_data(self, keyword1, keyword2, keyword3):
        index = self.index
        countries_count = []
        countries = ['KR', 'JP', 'US', 'EP']
        if keyword1 == "ALL":
            result = []
            for i in range(4):
                body = {
                    "query": {
                        "bool": {
                            "must": [{"match": {"국가코드": countries[i]}}, {"match": {"발명의 명칭": keyword2}}],
                            "should": [{"match": {"요약": keyword3}}]
                        }
                    },
                    "size": 500 
                }
                results = es.search(index=index, body=body)
                re_count = results['hits']['total']['value']
                countries_count.append(re_count)
                re_hits = results['hits']['hits']
                n = len(re_hits)
                for i in range(n):
                    data = re_hits[i]['_source']
                    result.append([data['국가코드'], data['출원일'], data['출원인'], data['발명의 명칭'], data['요약'], data['대표청구항'], re_hits[i]['_score']])
                re_count = sum(countries_count)
            return result, re_count, countries_count
        else:  # 나라별 검색 결과
            body = {
                "query": {
                    "bool": {
                        "must": [{"match": {"국가코드": keyword1}}, {"match": {"발명의 명칭": keyword2}}],
                        "should": [{"match": {"요약": keyword3}}]
                    }
                },
                "size": 500  # 검색되는 건수 제한
            }
            results = es.search(index=index, body=body)
            re_count = results['hits']['total']['value']
            re_hits = results['hits']['hits']
            n = len(re_hits)
            result = []
            for i in range(n):
                data = re_hits[i]['_source']
                result.append([data['국가코드'], data['출원일'], data['출원인'], data['발명의 명칭'], data['요약'], data['대표청구항'], re_hits[i]['_score']])
            for i in range(4):
                if keyword1 == countries[i]:
                    countries_count.append(re_count)
                else:
                    countries_count.append(0)
            return result, re_count, countries_count




    def search_all(self):
        index = self.index
        body = { "query" : { "match_all" : {} }, "size" : 1000}
        results = es.search(index=index, body=body)
        count = results['hits']['total']['value']
        re_hits = results['hits']['hits']
        n = len(re_hits)
        result = []
        for i in range(n):
            data = re_hits[i]['_source']
            result.append([data['국가코드'], data['출원일'], data['출원인'], data['발명의 명칭'], data['요약'], data['대표청구항'], '-'])
        return result, count

    def country_data(self):
        index = self.index
        x = [ 'KR', 'JP', 'US', 'EP']
        y = []
        for i in range(4):
            body = {
                "query": {
                    "match": { "국가코드" : x[i] }
                },
                "size": 500
            }
            results = es.search(index=index, body=body)
            re_hits = results['hits']['hits']
            n = len(re_hits)
            y.append(n)

        return x, y

class DataForGraph():
    """
    데이터 -> d3 그래프
    break - 카운트 후 다음 특허
    """
    def __init__(self, data):
        self.data = data

    def dataForLine(self):
        data = self.data
        result_kr = {1990: 0, 1995: 0, 2000: 0, 2005: 0, 2010: 0, 2015: 0, 2020: 0}
        result_jp = {1990: 0, 1995: 0, 2000: 0, 2005: 0, 2010: 0, 2015: 0, 2020: 0}
        result_us = {1990: 0, 1995: 0, 2000: 0, 2005: 0, 2010: 0, 2015: 0, 2020: 0}
        result_ep = {1990: 0, 1995: 0, 2000: 0, 2005: 0, 2010: 0, 2015: 0, 2020: 0}
        year = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
        for i in range(len(data)):
           app_data = int(data[i][1][:4])
           for j in range(7):
                if app_data <= year[j]:
                    if data[i][0] == 'KR':
                        result_kr[year[j]] = result_kr[year[j]]+1
                        break
                    elif data[i][0] == 'JP':
                        result_jp[year[j]] = result_jp[year[j]]+1
                        break
                    elif data[i][0] == 'US':
                        result_us[year[j]] = result_us[year[j]]+1
                        break
                    else:
                        result_ep[year[j]] = result_ep[year[j]]+1
                        break
        return result_kr, result_jp, result_us, result_ep
