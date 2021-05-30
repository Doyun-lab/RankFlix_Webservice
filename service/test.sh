if [ $# -lt 1 ]; then
        echo 'give 1 argument'
else
        if [ $1 = 'login' ]; then
                curl -H "Content-type: application/json" -X POST -d '{"user_id":"iam","passwd":"biggong"}' http://127.0.0.1:11100/login >> ret
        elif [ $1 = 'favorite' ]; then
                curl -H "Content-type: application/json" -X POST -d '{"session_id":"xxxxxxxx"}' http://127.0.0.1:11100/favorite >> ret
        fi
fi

