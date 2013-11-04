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

### Python and environment tools

For this project, we will use pyenv as a tool to manage our python versions and environments.  
To install pyenv, you can go take a look at the pages for [pyenv](https://github.com/yyuu/pyenv) and [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv).  

Using brew, you can install them by running
```
$ brew install pyenv pyenv-virtualenv  
$ echo 'if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi' >> ~/.bash_profile
```

Once you have pyenv installed, you can install python 2.7.5:
```
$ pyenv install 2.7.5
```

Finally, once you have pyenv installed, go to the directory where this repository is checked out and install python dependencies by running:
```
$ pip install -r requirements.txt
```
