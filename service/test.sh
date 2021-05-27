if [ $# -lt 1 ]; then
        echo 'give at least 1 argument'
Else
        if [ $1 = 'login' ]; then
                SESSION=$(curl -H "Content-type: application/json" -X POST -d '{"user_id":"iam","passwd":"biggong"}' http://127.0.0.1:11100/login)
                echo "$SESSION"
                echo "$SESSION" >> ret
        elif [ $1 = 'fav-add' ]; then
                statement='{"request_type":"add","session_id":"'$2'","favorite":["킹덤", "옥자"]}'
                echo "$statement"
                curl -H "Content-type: application/json" -X POST -d "$statement" http://127.0.0.1:11100/favorite >> ret
        fi
fi

