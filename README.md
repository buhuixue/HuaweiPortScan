# HuaweiPortScan
用于华为93系列交换机读取设备端口和光模块对应信息
#
使用方法：
#
1.使用以下命令保存日志文件
#
scr 0 tem  
dis inter br main  
dis transceiver  


#
2.使用脚本跑此日志文件即可得到结果
#
XGigabitEthernet4/0/3    XGigabitEthernet4/0/3    up        :10GBASE_LR_SFP       :1310   
XGigabitEthernet4/0/4    XGigabitEthernet4/0/4    up        :10GBASE_LR_SFP       :1310   
XGigabitEthernet4/0/5    XGigabitEthernet4/0/5    up        :10GBASE_LR_SFP       :1310   
XGigabitEthernet4/0/6    XGigabitEthernet4/0/6    up        :10GBASE_LR_SFP       :1310   
XGigabitEthernet3/0/1    XGigabitEthernet3/0/1    up        :10GBASE_LR_SFP       :1310   
GigabitEthernet1/0/0     GigabitEthernet1/0/0     up        :1000_BASE_LX_SFP     :1310

# huawei_port_check.py
用于华为93系列交换机读取设备端口和检查光模块收发光状态
通过检查display transceiver version命令的输出信息，判断端口收发光是否正常（*down接口不做检查）
#
使用方法：
1.使用以下命令保存日志文件
#
scr 0 tem  
dis inter br main  
dis transceiver 

#
2.使用脚本跑此日志文件输出csv文件
python huawei_port_check.py
