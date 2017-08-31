As per the documentation in https://github.com/git-lfs/git-lfs/wiki/Tutorial, following steps are outlined.


=============================================================================
install git-lfs

-  Debian

Debian 7 Wheezy and similar needs to have the backports repo installed to get git >= 1.8.2

echo 'deb http://http.debian.net/debian wheezy-backports main' > /etc/apt/sources.list.d/wheezy-backports-main.list
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install

-  Mac OSX

You may need to brew update to get all the new formulas
brew install git-lfs
git lfs install

-  RHEL/CentOS

Install git >= 1.8.2

Recommended method for RHEL/CentOS 5 and 7 (not 6!)

Install the epel repo link (For CentOS it's just sudo yum install epel-release)
sudo yum install git
Recommended method for RHEL/CentOS 6

Install the IUS Community repo. curl -s https://setup.ius.io/ | sudo bash or here
sudo yum install git2u
You can also build git from source and install it. If you do that, you will need to either manually download the the git-lfs rpm and install it with rpm -i --nodeps git-lfs*.rpm, or just use the Other instructions. The only other advanced way to fool yum is to create and install a fake/real git rpm to satisfy the git >= 1.8.2 requirement.

To install the git-lfs repo, run curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash from here

sudo yum install git-lfs

git lfs install

-  Ubuntu

Similar to Debian 7, Ubuntu 12 and similar Wheezy versions need to have a PPA repo installed to get git >= 1.8.2

sudo apt-get install software-properties-common to install add-apt-repository (or sudo apt-get install python-software-properties if you are on Ubuntu <= 12.04)
sudo add-apt-repository ppa:git-core/ppa
The curl script below calls apt-get update, if you aren't using it, don't forget to call apt-get update before installing git-lfs.
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install

-  Windows

Download the windows installer from here
Run the windows installer
Start a command prompt/or git for windows prompt and run git lfs install
Docker Recipes

- For Debian Distros, you can use

RUN build_deps="curl ca-certificates" && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${build_deps} && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git-lfs && \
    git lfs install && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -r /var/lib/apt/lists/*

-  Other

To install on any supported operating system, manually install git-lfs with no man pages.

Only one file is required for git-lfs, the git-lfs binary. i386 and x86_64 versions are available here for FreeBSD, Linux, Mac and Windows. Currently, linux arm6 must be compiled from source

Install git version 1.8.2 or newer
Download and put the git-lfs (.exe for windows) in your path, and git lfs commands start working, as long as both git and git-lfs are in your path.
Source

Get go. Either use your OS repo or get it here. For best results, use latest stable go to get all the patches
git clone https://github.com/github/git-lfs.git
In the git-lfs directory, run ./script/bootstrap
The git-lfs binary should appear in the ./bin directory
Alternatively, you can use go to

go get github.com/github/git-lfs
$GOPATH/bin/
Edit/checkout $GOPATH/src/github.com/github/git-lfs and run go build github.com/github/git-lfs if needed

=============================================================================
setup git-lfs with this project

To the current directory of your clones local repo of the concept-to-clinic.
Then execute the following commands.
-   git add .gitattributes


=============================================================================
decide to track files with git-lfs and remove those files from the repo

- git lfs track "prediction/src/algorithms/classify/assets/*"
- git lfs track "test/assets/*"

=============================================================================

not use git-lfs (for example, to save on bandwidth) and pull the repo without the large files

- git lfs pull
