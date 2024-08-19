[
   {
      "essential": true,
      "name":"flask-app",
      "image":"${REPOSITORY_URL}",
      "portMappings":[
         {
            "containerPort":9696,
            "hostPort":9696,
            "protocol":"tcp"
         }
      ],
      "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "${CLOUDWATCH_GROUP}",
            "awslogs-region": "${REGION}",
            "awslogs-stream-prefix": "ecs"
          }
        },
      "environment":[
         {
            "name":"FLASK_APP",
            "value":"${FLASK_APP}"
         },
         {
            "name":"FLASK_ENV",
            "value":"${FLASK_ENV}"
         },
         {
            "name":"APP_HOME",
            "value":"${FLASK_APP_HOME}"
         },
         {
            "name":"APP_PORT",
            "value":"${FLASK_APP_PORT}"
         },
         {
            "name":"AWS_ACCESS_KEY_ID",
            "value":"${AWS_ACCESS_KEY_ID}"
         },
         {
            "name":"AWS_SECRET_ACCESS_KEY",
            "value":"${AWS_SECRET_ACCESS_KEY}"
         }
      ]
   }
]
