from waitress import serve

import API_Controller

serve(API_Controller.app, host='10.2.1.21', port=9000)
