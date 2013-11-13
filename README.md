UP Research Mining
==================

Code that obtains insight from UP User Research Studies


Environment setup
-----------------

The tooling used for analysis includes python.  
We start with python environment management.  

### Package Manager

For Mac, you want to install homebrew. On linux distros your package manager should have the packages you want.  

You can find information about installing homebrew at [http://brew.sh/](http://brew.sh/).  

If you are in a hurry, you can type the following commands in a terminal:

```
$ curl -fsSLo go.rb https://raw.github.com/mxcl/homebrew/go  
$ ruby go.rb  
$ rm go.rb
```

### Postgres

We store data in Postgres for easy querying.

Please install postgres, either from your pacakge manager or from something like [Postgres.app](http://postgresapp.com/) on Mac OS X.  

Once you have installed Postgres, make sure pg_config is in your path, as you're going to need it to install the Python Postgres driver. If you installed Postgres.app, you can do so as follows:

```
$ export PATH=/Applications/Postgres93.app/Contents/MacOS/bin/:$PATH
```

### Python and environment tools

For this project, we will use pyenv as a tool to manage our python versions and environments.  
To install pyenv, you can go take a look at the pages for [pyenv](https://github.com/yyuu/pyenv)  

Using brew, you can install them by running
```
$ brew install pyenv  
$ echo 'if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi' >> ~/.bash_profile
$ . ~/.bash_profile
```

Once you have pyenv installed, you can install python 2.7.5:
```
$ pyenv install 2.7.5
```

Finally, once you have pyenv installed, go to the directory where this repository is checked out. Set up a virtualenv and install python dependencies by running:
```
$ pyenv local 2.7.5
$ pip install virtualenv
$ ./setup-project.sh
```
