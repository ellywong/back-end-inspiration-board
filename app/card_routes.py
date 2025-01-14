
from app import db
from app.models.board import Board
from app.models.card import Card
from flask import Blueprint, request, jsonify
import os 

card_bp = Blueprint("card", __name__, url_prefix="/cards")
board_bp = Blueprint("board", __name__, url_prefix="/boards")

# FE ACTION: Submit button on card
## Create a card 
# expected {"message": "loremipsum"} => error message or created card object
@card_bp.route("", methods=["POST"]) 
def create_card():
    try: 
        request_body = request.get_json()[0]
        message = request_body["message"]
        board_id = request_body["board_id"]
    
        if not message: 
            return {"details": "Message can not be empty"}, 400
        elif len(message) > 40: 
            return {"details": "Message exceeds 40 characters limit"}, 400
        else : 
            new_card = Card(
                message = message,
                likes_count = 0,
                board_id = board_id
            )
            db.session.add(new_card)
            db.session.commit() 
            response_body = build_a_card_response(new_card)
            return response_body, 201
        
    except KeyError as err:
        if "message" in err.args:
            return {"details": "Request must include a message."}, 400
        
        elif "board_id" in err.args:
            return {"details": "Request must include a board_id."}, 400
        

#Create card in ralation to a board         
@board_bp.route("/<board_id>/cards",methods=["POST"])
def create_board_card(board_id):
    board = Board.query.get(board_id)
    request_body = request.get_json()
    if not request_body or "message" not in request_body:
        return jsonify({"details": "Request must include a message."}), 400
    elif  len(request_body["message"]) < 1: 
        return jsonify({"details": "Message can not be empty"}), 400
    elif len(request_body["message"]) > 40: 
        return jsonify({"details": "Message exceeds 40 characters limit"}), 400
    else : 
        new_card = Card(
            message = request_body["message"],
            likes_count = 0
        )
        db.session.add(new_card)
        db.session.commit() 

        # # get the card id of the new card
    new_card_id = Card.query.get(new_card.card_id)
        # # inserting new card to the board
    board.cards.append(new_card_id)
        # response_body = {
        # “id”: new_card_id ,
        # “message”: new_card.message,
        # “likes_count”: new_card.likes_count,
        # }
        # return jsonify(response_body), 201
    response_body = build_a_card_response(new_card)
    return jsonify(response_body), 201

#FE Action: Click a board title => all cards related to that board id (dont need)
## Reads a single card with current message and likes count
# Expected: card_id # => error message or card object 
@card_bp.route("/<card_id>", methods=["GET"])
def show_likes_count(card_id):
    if not card_id.isnumeric():
        return jsonify({"details":f"{card_id} is invalid, card id must be numerical"}),400
    card = Card.query.get(card_id)
    if card == None:
        return jsonify({"details": f"Card {card_id} was not found"}), 404 
    else:
        response_body = build_a_card_response(card)
        return jsonify(response_body),200

#FE Action: +1 button on a card
# Updates a card likes count by 1 
## expected card_id# {likes_count: 1} => error message or updated card object
@card_bp.route("/<card_id>", methods=["PATCH"])
def update_likes_count(card_id):
    request_body = request.get_json()
    if not card_id.isnumeric():
        return jsonify({"details":f"{card_id} is invalid, card id must be numerical"}),400
    if not request_body or "likes_count" not in request_body:
        return jsonify({"details": "Request must include likes_count."}), 400
    card = Card.query.get(card_id)
    if card == None:
        return jsonify({"details": f"Card {card_id} was not found"}), 404 
    else:
        card.likes_count = card.likes_count + request_body["likes_count"]
    db.session.commit()
    response_body = build_a_card_response(card)
    return jsonify(response_body),200

#FE Action: delete button on a card 
# Delete specific card
# expected: card_id # => error message or success message 
@card_bp.route("/<card_id>", methods=["DELETE"])
def delete_specific_card(card_id):
    if not card_id.isnumeric():
        return jsonify({"details":f"{card_id} is invalid, card id must be numerical"}),400
    card = Card.query.get(card_id)
    if card == None:
        return jsonify({"details": f"Card {card_id} was not found"}), 404
    else:
        db.session.delete(card)
        db.session.commit()
        return jsonify({"details": f"Card {card_id} was successfully deleted"}), 200
    

@card_bp.route("/allcards", methods=["DELETE"])
def delete_all_cards():
    all_cards = Card.query.all()
    for card in all_cards:
        db.session.delete(card)
        db.session.commit()
    return {"details": "all cards were successfully deleted"}, 200
    

#FE Action: None 
#Testing card creation 
# Will need to get cards in relations to a board for project 
# expected:nothing => all card objects 
@card_bp.route("", methods = ["GET"])
def get_all_cards():
        cards = Card.query.all()
        response_body = build_cards_response(cards)
        return jsonify(response_body),200


##Helpers 
def build_a_card_response(card):
    response = {
        "id": card.card_id, 
        "message": card.message,
        "likes_count": card.likes_count,
        }
    return response

def build_cards_response(cards):
    response = []
    for card in cards:
        response.append({
        "id": card.card_id, 
        "message": card.message,
        "likes-count": card.likes_count,
        })
    return response 