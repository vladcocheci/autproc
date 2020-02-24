# docker build -t autproc .
# docker run -v <HOST_FOLDER>:/usr/src/autproc autproc 'yyyy' 'no_of_first_approval' 'no_of_last_approval'

FROM python:3.8-alpine
ADD scraper_autorizatii_cj.py /
ADD autproc.py /
ADD Pipfile /
ADD Pipfile.lock /

RUN apk add alpine-sdk
RUN mkdir -p ~/libpostal_data
RUN apk add curl autoconf automake libtool python-dev pkgconfig
RUN git clone https://github.com/openvenues/libpostal

RUN cd libpostal && ./bootstrap.sh && ./configure --datadir ~/libpostal_data && make && make install && ldconfig /

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

RUN ["python", "-c", "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"]

ENTRYPOINT ["python", "-u", "./scraper_autorizatii_cj.py"]
