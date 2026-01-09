llc()        { llcat -s "$LLC_SERVER" -k "$LLC_KEY" -m "$LLC_MODEL" "$@" }
llc-key()    { LLC_KEY=$1 }
llc-server() { LLC_SERVER=$1 }
llc-models() { LLC_MODEL=$(llcat -s "$LLC_SERVER" -k "$LLC_KEY" -m | fzf) }
