# -*- mode: ruby -*-
# vi: set ft=ruby :

arteriauser    = ENV['ST2USER'] ? ENV['ST2USER']: 'arteriaadmin'
arteriapasswd  = ENV['ST2PASSWORD'] ? ENV['ST2PASSWORD'] : 'arteriarulz'
st2version     = File.read('utils/st2.version.txt')

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.define "arteria" do |arteria|
    # Box details
    arteria.vm.box = "bento/ubuntu-14.04"
    arteria.vm.hostname = "arteria-dev"

    # Box Specifications
    arteria.vm.provider :virtualbox do |vb|
      vb.memory = 1028
      vb.cpus = 2
    end

    # Configure a private network
    arteria.vm.network :private_network, ip: "192.168.16.20"

    # Start shell provisioning.
    arteria.vm.provision "shell",
      inline: "sudo apt-get update && sudo apt-get install -y curl python-virtualenv vim"

    arteria.vm.provision "shell",
      inline: "curl -sSL https://stackstorm.com/packages/install.sh | bash -s -- --user=#{arteriauser} --password=#{arteriapasswd} --version=#{st2version}"

    arteria.vm.provision "shell",
      inline: "ln -s /vagrant /opt/stackstorm/packs/arteria"

  end

end
