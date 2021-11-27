FROM python:3.7
ENV APP_ROOT /code
WORKDIR ${APP_ROOT}/
COPY Pipfile ${APP_ROOT}/
COPY Pipfile.lock ${APP_ROOT}/
RUN pip install --no-cache-dir --trusted-host pypi.tuna.tsinghua.edu.cn -i https://pypi.tuna.tsinghua.edu.cn/simple/ pipenv
RUN pipenv install
ENV TIME_ZONE=Asia/Shanghai
RUN echo "${TIME_ZONE}" > /etc/timezone && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime
EXPOSE 6501/tcp
COPY . ${APP_ROOT}
RUN find . -name "*.pyc" -delete
CMD ["python","run.py"]