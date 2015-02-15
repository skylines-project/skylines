VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provider "virtualbox" do |v|
    v.memory = 512
    v.cpus = 1
    v.gui = true
  end

  config.vm.box = "chef/ubuntu-14.04"

  config.vm.network "forwarded_port", guest: 5000, host: 5000
end