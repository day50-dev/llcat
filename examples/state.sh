llf()        { llc "$@" 2> >(jq . >&2) 1> >(sd >&1) }
llc()        { llcat -m "$LLC_MODEL" -u "$LLC_SERVER" -k "$LLC_KEY" "$@" }
llc-model()  { LLC_MODEL=$(llcat -m  -u "$LLC_SERVER" -k "$LLC_KEY" | fzf) }
llc-server() { LLC_SERVER=$1 }
llc-key()    { LLC_KEY=$1 }
