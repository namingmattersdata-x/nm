# main application
require 'sinatra'
require 'csv'
# root path

get '/' do
    erb :index
    
end

get '/query/:input' do
    @input = params['input']
    @csv_data = CSV.read(@input + '.csv', headers:true)
    erb :result
end

post '/submit' do
    @query = params[:query]
    @industry = params[:industry]
    system("python pythonscript.py")
    destination = '/query/' + @query
    redirect destination
end