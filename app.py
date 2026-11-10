from flask import Flask, request, jsonify, make_response
import os
# ... (بقية الـ imports والوظائف كما هي)

@app.route('/gl', methods=['GET', 'POST'])
def gl_endpoint():
    """
    Endpoint format: /gl?teamcode=YOUR_TEAM_CODE
    """
    # جلب teamcode من الـ Query String
    team_code = request.args.get('teamcode')
    
    if not team_code:
        return make_response(jsonify({
            "status": "error",
            "message": "Missing teamcode parameter. Usage: /gl?teamcode=YOUR_CODE"
        }), 400)

    global BARRIER
    
    # إعداد الباريير بناءً على عدد الحسابات
    try:
        BARRIER = threading.Barrier(len(ACCOUNTS))
    except ValueError:
        return make_response(jsonify({"status": "error", "message": "No accounts configured"}), 500)

    threads = []
    results = []
    errors = []

    for acc_uid, acc_pass in ACCOUNTS:
        try:
            res = login_account(acc_uid, acc_pass)
            if res:
                state = {
                    "name": res["name"], 
                    "uid": str(res["uid"]), 
                    "token": res["token"],
                    "sent": 0, 
                    "online": False, 
                    "online2": False, 
                    "ready": False,
                }
                
                # تشغيل الثريدات
                t1 = threading.Thread(
                    target=_Session,
                    args=(res["ip"], res["port"], state, res["uid"], res["jwt"], res["ts"], res["key"], res["iv"], "online", "ChaT", team_code),
                    daemon=True,
                )
                t2 = threading.Thread(
                    target=_Session,
                    args=(res["ip2"], res["port2"], state, res["uid"], res["jwt"], res["ts"], res["key"], res["iv"], "chat", "OnLinE", team_code),
                    daemon=True,
                )
                
                t1.start()
                t2.start()
                threads.extend([t1, t2])
                results.append({"account": acc_uid, "name": res["name"], "status": "running"})
            else:
                errors.append({"account": acc_uid, "reason": "Login Failed"})
                
        except Exception as e:
            errors.append({"account": acc_uid, "error": str(e)})

    response_data = {
        "status": "success",
        "team_code_used": team_code,
        "accounts_active": len(results),
        "details": results,
        "errors": errors
    }
    
    return jsonify(response_data)

# ... (باقي الكود كما هو)