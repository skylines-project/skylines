#
# Author:: Tobias Bieniek (<tobias.bieniek@gmx.de>)
# Cookbook Name:: skylines
# Recipe:: database
#
# Copyright 2013, Tobias Bieniek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This is potentially destructive to the nodes mysql password attributes, since
# we iterate over all the app databags. If this database server provides
# databases for multiple applications, the last app found in the databags
# will win out, so make sure the databags have the same passwords set for
# the root, repl, and debian-sys-maint users.
#

# install the database server
include_recipe "postgresql::server"

# install fuzzystrmatch extension
include_recipe "postgresql::contrib"

# create database user
pg_user "vagrant" do
  privileges :login => true
end

# create databases
pg_database "skylines" do
  owner "vagrant"
  encoding "utf8"
  template "template0"
  locale "en_US.UTF8"
end

pg_database "skylines_test" do
  owner "vagrant"
  encoding "utf8"
  template "template0"
  locale "en_US.UTF8"
end

# add extensions to database
pg_database_extensions "skylines" do
  extensions ["fuzzystrmatch"]
  postgis true
end

pg_database_extensions "skylines_test" do
  extensions ["fuzzystrmatch"]
  postgis true
end
