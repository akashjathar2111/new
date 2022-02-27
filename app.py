import pandas as pd
import numpy as np
import streamlit as st
from pmdarima.arima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error


st.title('Import and Export of Various Commodities  by India')
choice = ['None','Import','Export']

z = st.sidebar.selectbox('Tread Flow',choice)

if z == 'None':
    pass
else:
    df1 = pd.read_csv(str(z)+str('_monthly11_15.csv'))
    df2 = pd.read_csv(str(z)+str('_monthly16_21.csv'))
    df = df1.append(df2)
    data = df
    del df
    data['Month']= pd.to_datetime(data['Month'])

    m = data['Commodity'].unique()

    commodity = st.sidebar.selectbox('Select Commodity',m)

    x = ['None','Value(INR)','Quantity']
    feature = st.selectbox('Select Feature',x)
    if feature == "None":
        pass

    elif feature == 'Value(INR)':


        #Total Export value of commodity per year
        Value_sum = data[data['Commodity']==commodity].groupby('Month')['value(INR)'].sum()
        value_sum = pd.DataFrame(round(Value_sum/10**8))
        train = value_sum[:110]
        test = value_sum[110:]

        #Arima Model
        model = auto_arima(train, start_p=1, start_q=1,
                    max_p=7, max_q=7,
                    m=12,  ######################################           
                    seasonal=True,   
                    start_P=0, 
                    D=None, 
                    trace=True,
                    error_action='ignore',  
                    suppress_warnings=True, 
                    stepwise=True)
        pred_arima = model.predict(len(test))
        RMSE1 = np.sqrt(mean_squared_error(test['value(INR)'],pred_arima))

        #Holt Winter's Model
        ### Holts winter exponential smoothing with additive seasonality and additive trend
        hwe_model_add_add = ExponentialSmoothing(value_sum,seasonal="add",trend="add",seasonal_periods=12).fit() #add the trend to the model
        pred_hwe_add_add = hwe_model_add_add.predict(start = test.index[0],end = test.index[-1])
        RMSE2 =np.sqrt(mean_squared_error(test['value(INR)'],pred_hwe_add_add))



        ### Holts winter exponential smoothing with multiplicative seasonality and additive trend
        hwe_model_mul_add = ExponentialSmoothing(value_sum,seasonal="mul",trend="add",seasonal_periods=12).fit() 
        pred_hwe_mul_add = hwe_model_mul_add.predict(start = test.index[0],end = test.index[-1])
        RMSE3 =np.sqrt(mean_squared_error(test['value(INR)'],pred_hwe_mul_add))


        st.dataframe({'Model':['ARIMA','Holt Winter with additive seasonality','Holt Winter with multiplicative seasonality'],'RMSE':[RMSE1,RMSE2,RMSE3]})
        x = [RMSE1,RMSE2,RMSE3]
        best_model = pd.Series(x).min()

        n = st.sidebar.slider('Forecasted',min_value=1,max_value=36)
        if best_model == RMSE1:
            order = model.order
            seasonal = model.seasonal_order

            X = train.values
            X = X.astype('float32')

            Arima = ARIMA(X,order=order,seasonal_order=seasonal)
            model_fit = Arima.fit()
            forecast = model_fit.forecast(steps = n)
            st.header( 'Forecasted Value(INR) by Arima Model in 10^8(INR) ')
            st.line_chart(forecast) 
    


        elif best_model == RMSE2:
            forecast = hwe_model_add_add.forecast(n)
            st.header("Forecasted Value(INR) by Holts winter's Additive seasonality in 10^8(INR)")
            st.line_chart(forecast) 


        elif best_model == RMSE3:
            forecast = hwe_model_mul_add.forecast(n)
            st.header("Forecasted Value(INR) by Holts winter's multiplicative seasonality in 10^8(INR)")
            st.line_chart(forecast)  





    elif feature == 'Quantity':
        
      
        #Total Export value of commodity per year
        Quantity = data[data['Commodity']==commodity].groupby('Month')['Qty'].sum() 
        unit = data[data['Commodity']==commodity]['Unit'].unique()
        Qty = pd.DataFrame(round(Quantity/1000,2))
        if str(unit) == '[nan]':
            st.write("Sorry We Don't Have Data of Quantity for perticular commodity")
        else:
            
        
            train = Qty[:110]
            test = Qty[110:]

            #Arima Model
            model = auto_arima(Qty, start_p=1, start_q=1,
                        max_p=7, max_q=7,
                        m=12,  ######################################           
                        seasonal=True,   
                        start_P=0, 
                        D=None, 
                        trace=True,
                        error_action='ignore',  
                        suppress_warnings=True, 
                        stepwise=True)
            pred_arima = model.predict(len(test))
            RMSE1 = np.sqrt(mean_squared_error(test,pred_arima))            


            #Holt Winter's Model
            ### Holts winter exponential smoothing with additive seasonality and additive trend
            hwe_model_add_add = ExponentialSmoothing(train,seasonal="add",trend="add",seasonal_periods=12).fit() #add the trend to the model
            pred_hwe_add_add = hwe_model_add_add.predict(start = len(train)+1,end = len(Qty))
            RMSE2 =np.sqrt(mean_squared_error(test,pred_hwe_add_add))



            ### Holts winter exponential smoothing with multiplicative seasonality and additive trend
            hwe_model_mul_add = ExponentialSmoothing(train,seasonal="mul",trend="add",seasonal_periods=12).fit() 
            pred_hwe_mul_add = hwe_model_mul_add.predict(start = len(train)+1,end = len(Qty))
            RMSE3 =np.sqrt(mean_squared_error(test,pred_hwe_mul_add))

            st.dataframe({'Model':['ARIMA','Holt Winter with additive seasonality','Holt Winter with multiplicative seasonality'],'RMSE':[RMSE1,RMSE2,RMSE3]})
            x = [RMSE1,RMSE2,RMSE3]
            n = st.sidebar.slider('Forecasted',min_value=1,max_value=50)
            best_model = pd.Series(x).min()
            if best_model == RMSE1:
                order = model.order
                seasonal = model.seasonal_order

                X = Qty.values
                X = X.astype('float32')

                Arima = ARIMA(X,order=order,seasonal_order=seasonal)
                model_fit = Arima.fit()
                forecast = model_fit.forecast(steps = n)
                st.header(f'Quantity (in{unit})')
                st.header("Forecasted by ARIMA Model")
                st.line_chart(forecast)



            elif best_model == RMSE2:
                forecast = hwe_model_add_add.forecast(n)
                st.header(f'Quantity (in{unit})')
                st.header("Forecasted by Holts winter's Additive seasonality ")
                st.line_chart(forecast)


            elif best_model == RMSE3:
                forecast = hwe_model_mul_add.forecast(n) 
                st.header(f'Quantity (in{unit})')
                st.header("Forecasted by Holts winter's multiplicative seasonality ")
                st.line_chart(forecast) 








    def country(Commodity):
    # for how many country India export this commodity per year
        country_count = data[data['Commodity']==Commodity].groupby('Month')['Country'].count() 

        st.header(f'Country Count of Tread for {commodity}')
        st.line_chart(country_count)
    country(commodity)
