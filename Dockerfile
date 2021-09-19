RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN python main.py