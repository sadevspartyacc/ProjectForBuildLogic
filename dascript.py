from flask import Flask, request, jsonify

app = Flask(__name__)

# Store last output states (default all zeros)
last_outputs = {f"d{i}": 0 for i in range(8)}

# Queue of characters to process
char_queue = []
current_message = ""
processing_complete = False
is_processing = False

# abdhp6 rule: a=1 (bit0), b=2 (bit1), d=4 (bit2), h=8 (bit3), p=16 (bit4), 6=32 (bit5)

def apply_abdhp6_rule(char_ascii):
    """Apply abdhp6 rule to ASCII character"""
    # Extract bits
    bit0 = (char_ascii >> 0) & 1  # a
    bit1 = (char_ascii >> 1) & 1  # b
    bit2 = (char_ascii >> 2) & 1  # d
    bit3 = (char_ascii >> 3) & 1  # h
    bit4 = (char_ascii >> 4) & 1  # p
    bit5 = (char_ascii >> 5) & 1  # 6
    
    # Build new byte with abdhp6 mapping
    new_byte = 0
    new_byte |= (bit0 << 0)  # a -> d0
    new_byte |= (bit1 << 1)  # b -> d1
    new_byte |= (bit2 << 2)  # d -> d2
    new_byte |= (bit3 << 3)  # h -> d3
    new_byte |= (bit4 << 4)  # p -> d4
    new_byte |= (bit5 << 5)  # 6 -> d5
    
    return new_byte

@app.route('/poll_chat', methods=['GET'])
def poll_chat():
    global last_outputs, char_queue, current_message, processing_complete, is_processing
    
    incoming_msg = request.args.get('msg')
    
    if incoming_msg and incoming_msg != current_message:
        char_queue = list(incoming_msg)
        current_message = incoming_msg
        processing_complete = False
        is_processing = True
        last_outputs = {f"d{i}": 0 for i in range(8)}
    
    if char_queue and is_processing:
        current_char = char_queue.pop(0)
        ascii_val = ord(current_char)
        transformed_value = apply_abdhp6_rule(ascii_val)
        binary_str = f"{transformed_value:08b}"
        
        new_outputs = {}
        for i in range(8):
            new_outputs[f"d{i}"] = int(binary_str[7-i])
        
        new_outputs["d6"] = 1  # Set d6=1 when text is being processed
        last_outputs = new_outputs
        
        if not char_queue:
            processing_complete = True
            is_processing = False
    
    return jsonify({
        "outputs": last_outputs,
        "status": "processing" if is_processing else ("complete" if processing_complete else "idle"),
        "queue_remaining": len(char_queue),
        "current_message": current_message,
        "processed": len(current_message) - len(char_queue) if current_message else 0,
        "total": len(current_message) if current_message else 0
    })

@app.route('/reset', methods=['GET'])
def reset():
    global last_outputs, char_queue, current_message, processing_complete, is_processing
    last_outputs = {f"d{i}": 0 for i in range(8)}
    char_queue = []
    current_message = ""
    processing_complete = False
    is_processing = False
    return jsonify({"status": "reset"})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "outputs": last_outputs,
        "queue_length": len(char_queue),
        "current_message": current_message,
        "is_processing": is_processing,
        "complete": processing_complete
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "404", "endpoints": ["/poll_chat?msg=text", "/status", "/reset"]}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)