#
# Author:: Tobias Bieniek (<tobias.bieniek@gmx.de>)
# Cookbook Name:: skylines
# Recipe:: weberror-fix
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

weberror_folder = "/usr/local/lib/python2.7/dist-packages/WebError-0.10.3-py2.7.egg/EGG-INFO"

file "#{weberror_folder}/top_level.txt" do
	mode "644"
end

file "#{weberror_folder}/requires.txt" do
	mode "644"
end

file "#{weberror_folder}/entry_points.txt" do
	mode "644"
end
