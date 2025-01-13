alias b := build
alias i := install

default:
    @just --list

build:
    rm -rf .flatpak-builder builddir repo
    flatpak-builder --force-clean --user --install-deps-from=flathub --repo=repo builddir org.techtowers.CloudSurge.json
    flatpak build-bundle repo cloudsurge.flatpak org.techtowers.CloudSurge

install: build
    flatpak install cloudsurge.flatpak
