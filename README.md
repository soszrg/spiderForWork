==========================================================================================
***********server deploy**********
1.version [server] ccnet-4.3.0 seafile-4.3.0 seahub-4.3.0-server libsearpc-3.0-latest
[client]
4.28

2.dependencies(in ubuntu) url:http://manual.seafile.com/build_seafile/server.html
(1)preparation
	libevent-dev (2.0 or later )
	libcurl4-openssl-dev (1.0.0 or later)
	libglib2.0-dev (2.28 or later)
	uuid-dev
	intltool (0.40 or later)
	libsqlite3-dev (3.7 or later)
	libmysqlclient-dev (5.5 or later)
	libarchive-dev
	libtool
	libjansson-dev
	valac
	libfuse-dev
	python-dev
	mysql-server 
	mysql-client 
	libmysqlclient-dev 

	sudo apt-get install libevent-dev libcurl4-openssl-dev libglib2.0-dev uuid-dev intltool libsqlite3-dev libmysqlclient-dev libarchive-dev libtool libjansson-dev valac libfuse-dev python-dev mysql-server mysql-client libmysqlclient-dev 

(2)libzdb
    Install re2c and flex
    Download libzdb:http://www.tildeslash.com/libzdb/dist/libzdb-2.12.tar.gz

(3)libevhtp
    Download libevhtp:https://github.com/ellzey/libevhtp/archive/1.1.6.zip
    Build libevhtp by:
    cmake -DEVHTP_DISABLE_SSL=ON -DEVHTP_BUILD_SHARED=ON .
    make
    sudo make install

(4)seahub dependencies
    django 1.5:https://www.djangoproject.com/download/1.5.2/tarball/
    djblets:https://github.com/djblets/djblets/tarball/release-0.6.14
    sqlite3
    simplejson (python-simplejson)
    PIL (aka. python imaging library, python-image)
    chardet
    gunicorn
    django-compressor==1.4
    django-statici18n==1.1.2
    six
    python-dateutil
    pyes
    MySQL-python
    django-taggit 
    pyelasticsearch
    urlib3(beacause pyes may cover urllib3, check where there is src dir of urllib3 in /usr/local/lib/pythonX.X/dist-package. If no, install it)
(5)install and config tomcat
	1):download tomcat6:http://tomcat.apache.org/
	2):extact, eg:/home/zrg/
	3):mv apache-tomcat-6.0.44 tomcat6
	4):create auditlog db
		CREATE DATABASE logaudit CHARACTER SET utf8 COLLATE utf8_bin;
		CREATE TABLE `audit` (
		  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		  `appID` varchar(64) DEFAULT NULL,
		  `appVersion` varchar(64) DEFAULT NULL,
		  `fileID` varchar(200) NOT NULL,
		  `fileName` varchar(200) NOT NULL,
		  `filePath` varchar(100) NOT NULL,
		  `opDate` datetime NOT NULL,
		  `opUser` varchar(200) NOT NULL,
		  `opType` varchar(200) NOT NULL,
		  `message` varchar(1024) DEFAULT NULL,
		  `macIP` varchar(200) NOT NULL,
		  `devInfo` varchar(200) DEFAULT NULL,
		  PRIMARY KEY (`id`,`opDate`)
		) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
	5):config env
		1)sudo vi /etc/profile
			add the following:
				export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/ (confirm java path and version)
				export CLASSPATH=$CLASSPATH:%JAVA_HOME/lib/tools.jar
				export TOMCAT_HOME=/home/zrg/tomcat6
				export CATALINA_HOME=$TOMCAT_HOME
				export PATH=$PATH:$TOMCAT_HOME/bin
		2)cd /home/zrg/tomcat6/bin
			vi catalina.sh
			add the following before cygwin=false
				JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/
		3)add audit.war into tomcat webapp
			mv ~/audit.war ~/tomcat6/webapps
		4)into tomcat/bin dir, start tomcat
			sudo ./startup.sh
			(sudo ./shutdown.sh to stop tomcat)
		5)modify audit ip
			cd ~/tomcat6/webapps/audit/WEB-INF/classes
			vi db.properties
			modify url to jdbc:mysql://localhost:3306/logaudit
			
3.compile and install components
    <1>dir structure
        ->baseline
        |   ->secfileServer
        |   |   ->seahub
        |   |   ->src
        |   |   |   ->ccnet
        |   |   |   ->libsearpc
        |   |   |   ->seafile
    <2>cd libsearpc
        ./autogen.sh
        ./configure
        make
        make install
    <3>cd ccnet
        ./autogen.sh
        export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
        ./configure --disable-client --enable-server
        make
        make install
    <4>cd seafile
       ./autogen.sh
        ./configure --disable-client --enable-server
        make
        make install
    <5>collect static css file.
        a)设定环境变量
            在/baseline/secfileServer/seahub/目录下有个setenv.sh.template模板 ,内容如下:
                export CCNET_CONF_DIR=/home/plt/dev/ccnet/seafile/tests/basic/conf2
                export SEAFILE_CONF_DIR=/home/plt/dev/ccnet/seafile/tests/basic/conf2/seafile-data
                export PYTHONPATH=/opt/lib/python2.6/site-packages:thirdpart:$PYTHONPATH
            复制上述文件为setenv.sh,并将上边环境变量的目录地址修改为baseline/src目录,如下示例：   
                export CCNET_CONF_DIR=/home/changyanjie/baseline_new/baseline/secfileServer/src/seafile/tests/basic/conf2
                export SEAFILE_CONF_DIR=/home/changyanjie/baseline_new/baseline/secfileServer/src/seafile/tests/basic/conf2/seafile-data
                export PYTHONPATH=/usr/lib/python2.6/site-packages:thirdpart:$PYTHONPATH
            运行 . setenv.sh 

        b)收集静态文件 
            在baseline/secfileServer/seahub/目录下执行./manage.py collectstatic --noinput
    
4.config mysql database 
	(1) create db and user
		create database `ccnet-db` character set = 'utf8'; 
		create database `seafile-db` character set = 'utf8'; 
		create database `seahub-db` character set = 'utf8';

		create user 'seafile'@'localhost' identified by 'seafile';
		GRANT ALL PRIVILEGES ON `ccnet-db`.* to `seafile`;
		GRANT ALL PRIVILEGES ON `seafile-db`.* to `seafile`;
		GRANT ALL PRIVILEGES ON `seahub-db`.* to `seafile`;
	(2) config server info
		cd baseline
		export PYTHONPATH=[baseline path]/baseline/secfileServer/seahub/thirdpart
		secfile-admin setup //config server(when hint that[You just installed Django's auth system, which means you don't have any superusers defined.],input "no")
	(2)modify ccnet/ccnet.conf, Add
		[Database]
		ENGINE=mysql
		HOST=localhost
		USER=seafile
		PASSWD=seafile
		DB=ccnet-db
	(3)modify seafile-data/seafile.conf, Add
		[database]
		type=mysql
		host=localhost
		user=seafile
		password=seafile
		db_name=seafile-db
	(4) modify seahub_settings.py, Add
		DATABASES = {
			'default': {
				'ENGINE': 'django.db.backends.mysql',
				'NAME' : 'seahub-db',
				'USER' : 'seafile',
				'PASSWORD' : 'seafile',
				'HOST' : 'localhost',
			}
		}
	(5)secfile-admin stop && secfile-admin start
5.create admin account
	1) export all sql files of [~/baseline/secfileServer/seahub/sql] into mysql db(if any error, maybe ignore it):eg.[mysql -uroot -p123456<mod-2015-08-04.sql]
	2) secfile-admin create-admin

6. add the following task into crontab to clear outdated file:
	1)crontab -e // open crontab config file
	2)0 1 * * * [baseline absolute path]/baseline/secfileServer/seahub/manage.py clearexfile	

7.install elasticsearch 
	1) install java env 
		sudo apt-get install default-jre default-jdk 
	2) download SearchEngine 
	3) start elasticsearch 
		./SearchEngine/bin/elasticsearch
///////////////here the server can work, the following is extra config///////////////

8.deploy server with auto script 
	1)deploy new server 
		a)copy autoDeploy.sh to parent dir of baseline dir 
			->XXX 
			|->baseline 
			|->autoDeploy.sh 
		b)execute shell script and input mysql root password, then input "y" to deploy a new server 
	2) update component(s) 
		a)as the 1)a) 
		b)mkdir temp dir and git new code in temp dir 
		c)execute shell and input mysql root password, then input "n" to update component 
		d)choose the component you want to update by inputing "y" when hint to input y/n
		
9.how to change language in webui 
	cd seahub/locale/LC_MESSAGES msgfmt -o django.mo django.po [if there isn't django.mo, in secfileServer/seahub, execute "./i18n compile-all"]
	#restart server
	secfile-admin stop
	secfile-admin start
	
10.how to use email server modify seahub_setting.py, Add
	EMAIL_USE_TLS = False
	EMAIL_HOST = 'smtp.domain.com'
	EMAIL_HOST_USER = 'username@domain.com'
	EMAIL_HOST_PASSWORD = 'password'
	EMAIL_PORT = 25
	DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
	SERVER_EMAIL = EMAIL_HOST_USER

	for 163, it,s like:
	EMAIL_USE_TLS = False
	EMAIL_HOST = 'smtp.163.com'
	EMAIL_HOST_USER = 'root@163.com'
	EMAIL_HOST_PASSWORD = '123456'
	EMAIL_PORT = 25
	DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
	SERVER_EMAIL = EMAIL_HOST_USER

	注意：163，需要到root@163.com账户去开启smtp服务，开启这个服务才可以使用email功能，
	若中间使用了授权码，这地方的password 就不在是登录密码， 是授权密码。

=============================================================================
***********Linux client deploy**********
depends:
	apt-get install autoconf automake libtool libevent-dev libcurl4-openssl-dev libgtk2.0-dev uuid-dev intltool libsqlite3-dev valac libjansson-dev libqt4-dev cmake libfuse-dev
1:set paths
	export PREFIX=/usr
	export PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
	export PATH="$PREFIX/bin:$PATH"

2:compile libsearpc
	cd libsearpc
	./autogen.sh
	./configure --prefix=$PREFIX
	make
	cd ..

3:compile ccnet
	cd ccnet
	./autogen.sh
	./configure --prefix=$PREFIX
	make
	
	
4:compile seafile
	cd seafile
	./autogen.sh
	./configure --prefix=$PREFIX --disable-gui
	make
	cd ..

5:compile seafile-client
	cd seafile-client
	cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PREFIX .
	make
	cd ..

6:make deb
	1) remove old file 
		rm seafile_0.0.2/usr/bin* 
		rm seafile_0.0.2/usr/lib/so 
		rm seafile_0.0.2/usr/lib/python2.7/dist-packages/ccnet/* -rf 
		rm seafile_0.0.2/usr/lib/python2.7/dist-packages/pysearpc/* -rf 
		rm seafile_0.0.2/usr/lib/python2.7/dist-packages/seafile/* -rf 
		rm seafile_0.0.2/usr/lib/python2.7/dist-packages/seaserv/* -rf

	2) cp new file to
		cp ccnet,ccnet-init,ccnet-tool to /usr/bin from ../secfileServer/src/ccnet after complie
		cp seaf-cli,seaf-daemon,seafile-applet to /usr/bin from ../secfileServer/src/seafile after complie
		cp libccnet.so.0.0.0, libseafile.so.0.0.0,libsearpc.so.1.0.2 to usr/lib from ../secfileServer/src/ ccnet seafile libsearpc, 
		and create link file
			ln -s libccnet.so.0.0.0 libccnet.so
			ln -s libccnet.so.0.0.0 libccnet.so.0 
			ln -s libseafile.so.0.0.0 libseafile.so
			ln -s libseafile.so.0.0.0 libseafile.so.0 
			ln -s libsearpc.so.1.0.2 libsearpc.so
			ln -s libsearpc.so.1.0.2 libsearpc.so.1
		cp python file to python2.7 dir 
			cp ccnet/python/ccnet/* /usr/lib/python2.7/dist-packages/ccnet/ 
			cp libsearpc/pysearpc/* /usr/lib/python2.7/dist-packages/pysearpc/ 
			cp seafile/python/seafile /usr/lib/python2.7/dist-packages/seafile 
			cp seafile/python/seaserv /usr/lib/python2.7/dist-packages/seaserv

	3)last step sudo dpkg -b secfile_0.0.2	
	
[comemnt]
	baseline/secfileServer/src/ccnet$ cp tools/ccnet-init cli/ccnet-tool net/daemon/ccnet ../../../secfileClient/linux/releaseDeb/v_0.0.1/secfile_0.0.2/usr/bin/
	baseline/secfileServer/src/seafile$ cp app/seaf-cli daemon/seaf-daemon ../../../secfileClient/linux/seafile-client/seafile-applet ../../../secfileClient/linux/releaseDeb/v_0.0.1/secfile_0.0.2/usr/bin/
	baseline/secfileServer/src/seafile$ cp lib/.libs/libseafile.so.0.0.0 ../ccnet/lib/.libs/libccnet.so.0.0.0 ../libsearpc/lib/.libs/libsearpc.so.1.0.2 ../../../secfileClient/linux/releaseDeb/v_0.0.1/secfile_0.0.2/usr/lib/
	ln -s 

	baseline/secfileClient/linux/releaseDeb/v_0.0.1/secfile_0.0.2/usr/lib/python2.7/dist-packages$ cp ../../../../../../../../../secfileServer/src/libsearpc/pysearpc/* pysearpc/ -r
	baseline/secfileClient/linux/releaseDeb/v_0.0.1/secfile_0.0.2/usr/lib/python2.7/dist-packages$ cp ../../../../../../../../../secfileServer/src/ccnet/python/ccnet/* ./ccnet/ -r
	baseline/secfileClient/linux/releaseDeb/v_0.0.1/secfile_0.0.2/usr/lib/python2.7/dist-packages$ cp ../../../../../../../../../secfileServer/src/seafile/python/seaserv/* ./seaserv/ -r