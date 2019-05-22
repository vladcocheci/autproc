# docker run -v <HOST_FOLDER>:/usr/src/autproc autproc 'yyyy' 'no_of_first_approval' 'no_of_last_approval'
FROM python:3.7-slim
WORKDIR /usr/src/autproc
ADD scraper_autorizatii_cj.py /
ADD autproc.py /

RUN pip3 install nltk pandas datetime bs4
RUN ["python", "-c", "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"]
ENTRYPOINT ["python", "./scraper_autorizatii_cj.py"]
