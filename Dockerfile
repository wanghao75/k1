#FROM swr.cn-north-4.myhuaweicloud.com/openeuler/aarch64/openeuler:20.03-lts-sp3
FROM swr.cn-north-4.myhuaweicloud.com/openeuler/openjdk/11-jdk-stretch:20.03-lts-sp1(3)
RUN yum install -y wget openssh-clients git \

RUN arch="$(arch)"; \
	yum install -y http://121.36.53.23/SP2/libabigail-1.6-4.oe1.$arch.rpm; \
	yum install -y http://121.36.53.23/SP2/perl-XML-Structured-1.3-2.oe1.$arch.rpm

ARG VERSION=4.3
ARG user=jenkins
ARG AGENT_WORKDIR=/home/${user}/agent

RUN yum install -y openssh-clients git curl \
    && mkdir /root/.ssh/ \
    && git clone https://${mygituser}:${mygitpwd}@gitee.com/wangchong1995924/lao_wang_9527 \
    && mv lao_wang_9527/super_publish_rsa /root/.ssh/ \
    && rm -rf lao_wang_9527

RUN curl --create-dirs -fsSLo /usr/share/jenkins/agent.jar https://repo.jenkins-ci.org/public/org/jenkins-ci/main/remoting/${VERSION}/remoting-${VERSION}.jar \
    && chmod 755 /usr/share/jenkins \
    && chmod 644 /usr/share/jenkins/agent.jar \
    && ln -sf /usr/share/jenkins/agent.jar /usr/share/jenkins/slave.jar

RUN curl --create-dirs -fsSLo /usr/local/bin/jenkins-agent http://121.36.53.23/AdoptOpenJDK/jenkins-agent

RUN chmod a+rx /usr/local/openjdk-11 \
     && chmod a+rx /usr/local/bin/jenkins-agent \
     && ln -s /usr/local/bin/jenkins-agent /usr/local/bin/jenkins-slave

ENV AGENT_WORKDIR=${AGENT_WORKDIR}
RUN mkdir /home/${user}/.jenkins && mkdir -p ${AGENT_WORKDIR}

WORKDIR ${AGENT_WORKDIR}
ENTRYPOINT ["jenkins-agent"]