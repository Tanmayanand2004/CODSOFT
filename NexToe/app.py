from flask import Flask, render_template, request, jsonify
from minimax import MinimaxAI
import json

app = Flask(__name__)

# Initialize the AI
ai_player = MinimaxAI()

@app.route('/')
def index():
    """Render the main game page"""
    return render_template('index.html')

@app.route('/api/move', methods=['POST'])
def make_move():
    """Handle player move and return AI response"""
    try:
        data = request.get_json()
        if not data:
            print("Error: No JSON data received")
            return jsonify({'error': 'No data received'}), 400
            
        board = data.get('board', [])
        position = data.get('position', -1)
        player = data.get('player', 'X')
        
        print(f"Received: board={board}, position={position}, player={player}")
        
        # Validate input
        if not board or len(board) != 9:
            print(f"Error: Invalid board state - length: {len(board) if board else 'None'}")
            return jsonify({'error': 'Invalid board state'}), 400
        
        # Handle AI first move (when position is -1)
        if position == -1:
            print("Handling AI first move")
            ai_symbol = 'O' if player == 'X' else 'X'
            ai_move = ai_player.get_best_move(board, ai_symbol)
            
            if ai_move is not None:
                board[ai_move] = ai_symbol
                
            return jsonify({
                'board': board,
                'ai_move': ai_move,
                'game_over': False,
                'winner': None,
                'winning_line': None
            })
            
        if position < 0 or position > 8:
            print(f"Error: Invalid position {position}")
            return jsonify({'error': f'Invalid position: {position}'}), 400
            
        if board[position] != '':
            print(f"Error: Position {position} already occupied with '{board[position]}'")
            return jsonify({'error': f'Position {position} already occupied'}), 400
        
        # Make player move
        board[position] = player
        
        # Check if game is over after player move
        game_status = check_game_status(board)
        if game_status['is_over']:
            return jsonify({
                'board': board,
                'game_over': True,
                'winner': game_status['winner'],
                'winning_line': game_status['winning_line']
            })
        
        # Get AI move
        ai_symbol = 'O' if player == 'X' else 'X'
        ai_move = ai_player.get_best_move(board, ai_symbol)
        
        if ai_move is not None:
            board[ai_move] = ai_symbol
            
        # Check game status after AI move
        game_status = check_game_status(board)
        
        return jsonify({
            'board': board,
            'ai_move': ai_move,
            'game_over': game_status['is_over'],
            'winner': game_status['winner'],
            'winning_line': game_status['winning_line']
        })
        
    except Exception as e:
        print(f"Error in make_move: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game board"""
    return jsonify({
        'board': [''] * 9,
        'game_over': False,
        'winner': None,
        'winning_line': None
    })

def check_game_status(board):
    """Check if the game is over and return winner info"""
    # Winning combinations
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    
    # Check for winner
    for combo in winning_combinations:
        if (board[combo[0]] != '' and 
            board[combo[0]] == board[combo[1]] == board[combo[2]]):
            return {
                'is_over': True,
                'winner': board[combo[0]],
                'winning_line': combo
            }
    
    # Check for draw
    if '' not in board:
        return {
            'is_over': True,
            'winner': 'draw',
            'winning_line': None
        }
    
    # Game continues
    return {
        'is_over': False,
        'winner': None,
        'winning_line': None
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
