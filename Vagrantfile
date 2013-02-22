Vagrant::Config.run do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  config.vm.forward_port 8080, 8080

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = [".cookbooks", "cookbooks"]
    
    chef.add_recipe "skylines"

    chef.json = {
    	postgresql: {
    		version: "9.1",

    		password: {
    			postgres: "postgres"
    		},
    	}
    }
  end
end