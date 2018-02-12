STANO2STASTR = {
    1:"未发货",
    2:"已提货",
    3:"在途中",
    4:"已签收",
    5:"已出票",
    6:"已收款",
}

STASTR2STANO = {
    "未发货":1,
    "已提货":2,
    "在途中":3,
    "已签收":4,
    "已出票":5,
    "已收款":6,
}

function order_status_switch(a){
    if(isNaN(a))
        return STASTR2STANO[a];
    else
        return STANO2STASTR[a];
}