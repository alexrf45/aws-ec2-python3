{
  description = "nix-labs :: aws python sdk — disposable development shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      tools = with pkgs; [
        # binary / exploitation
        python3
        python3Packages.ropper
        checksec
        file
        # recon / net
        nmap
        netcat-gnu
        ffuf
        # shell staples
        ripgrep
        jq
        curl
        wget
      ];
      # oh-my-zsh config baked into a read-only store dir, used as ZDOTDIR.
      zdotdir = pkgs.writeTextDir ".zshrc" ''
        export ZSH="${pkgs.oh-my-zsh}/share/oh-my-zsh"
        ZSH_THEME="aussiegeek"
        zstyle ':omz:update' mode disabled
        plugins=(git)

        # ZDOTDIR is a read-only store path — redirect every write to a cache dir.
        export ZSH_CACHE_DIR="''${XDG_CACHE_HOME:-$HOME/.cache}/nix-labs-zsh"
        mkdir -p "$ZSH_CACHE_DIR"
        export ZSH_COMPDUMP="$ZSH_CACHE_DIR/zcompdump"
        export HISTFILE="$ZSH_CACHE_DIR/history"
        export ZSH_DISABLE_COMPFIX=true

        source $ZSH/oh-my-zsh.sh

        # ---- inlined from ~/.commands ----
        extract() {
          if [ -f "$1" ]; then
            case "$1" in
              *.tar.bz2) tar xjf "$1" ;;
              *.tar.gz)  tar xzf "$1" ;;
              *.bz2)     bunzip2 "$1" ;;
              *.rar)     rar x "$1" ;;
              *.gz)      gunzip "$1" ;;
              *.tar)     tar xf "$1" ;;
              *.tbz2)    tar xjf "$1" ;;
              *.tgz)     tar xzf "$1" ;;
              *.zip)     unzip "$1" ;;
              *.Z)       uncompress "$1" ;;
              *.7z)      uncompress "$1" ;;
              *.apk)     uncompress "$1" ;;
              *.tar.lz)  uncompress "$1" ;;
              *.war)     uncompress "$1" ;;
              *.xz)      xz -d -v "$1" ;;
              *)         echo "'$1' cannot be extracted via extract()" ;;
            esac
          else
            echo "'$1' is not a valid file"
          fi
        }
        timestamp() {
          date +%Y%m%d-%T
        }

        alias v='vim'
        alias c='clear'
        alias q='exit'
        alias r='source $ZDOTDIR/.zshrc'
        alias d='docker'
        alias dc='docker container'
        alias dim='docker image'
        alias dimls='docker image ls'
        alias py='python3'
      '';
    in {
      devShells.default = pkgs.mkShell {
        name = "ctf";
        packages = tools ++ [pkgs.zsh];
        shellHook = ''
          echo "  disposable shell for developing code in this repo."

          # Interactive entry drops into zsh (oh-my-zsh); bash stays the
          # non-interactive default so direnv / `nix develop -c CMD` are unaffected.
          if [[ $- == *i* ]] && [ -t 1 ] && [ -z "''${NIX_LABS_ZSH:-}" ]; then
            export NIX_LABS_ZSH=1
            export ZDOTDIR="${zdotdir}"
            exec zsh
          fi
        '';
      };
      formatter = pkgs.alejandra;
    });
}
