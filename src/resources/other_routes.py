@app.route('/', methods=["GET"])
def index():
    '''
    Test Endpoint
    '''
    return Response(
        mimetype="application/text",
        response="sweet cheeks",
        status=418
    )


@app.route('/government-secrets', methods=["GET"])
def index_2():
    '''
    Test Endpoint
    '''
    return Response(
        mimetype="application/text",
        response="uh oh",
        status=451
    )
