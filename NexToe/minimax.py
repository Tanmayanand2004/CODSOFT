import math
import copy

class MinimaxAI:
    """
    Minimax AI implementation with Alpha-Beta Pruning for Tic-Tac-Toe
    """
    
    def __init__(self, use_alpha_beta=True):
        self.use_alpha_beta = use_alpha_beta
        self.winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
    
    def get_best_move(self, board, ai_symbol):
        """
        Ultra-fast AI using immediate pattern recognition
        """
        if '' not in board:
            return None
        
        human_symbol = 'X' if ai_symbol == 'O' else 'O'
        
        # Instant win check
        for i in range(9):
            if board[i] == '':
                board[i] = ai_symbol
                if self.check_winner(board) == ai_symbol:
                    board[i] = ''
                    return i
                board[i] = ''
        
        # Instant block check
        for i in range(9):
            if board[i] == '':
                board[i] = human_symbol
                if self.check_winner(board) == human_symbol:
                    board[i] = ''
                    return i
                board[i] = ''
        
        # Strategic moves (instant lookup)
        empty_positions = [i for i in range(9) if board[i] == '']
        
        # Center first
        if 4 in empty_positions:
            return 4
        
        # Corners next
        corners = [0, 2, 6, 8]
        for corner in corners:
            if corner in empty_positions:
                return corner
        
        # Any remaining position
        return empty_positions[0] if empty_positions else None
    
    def minimax(self, board, depth, is_maximizing, ai_symbol):
        """
        Standard Minimax algorithm
        """
        # Check terminal states
        winner = self.check_winner(board)
        if winner == ai_symbol:
            return 10 - depth
        elif winner and winner != ai_symbol:
            return depth - 10
        elif self.is_board_full(board):
            return 0
        
        if is_maximizing:
            max_score = -math.inf
            for i in range(9):
                if board[i] == '':
                    board[i] = ai_symbol
                    score = self.minimax(board, depth + 1, False, ai_symbol)
                    board[i] = ''
                    max_score = max(score, max_score)
            return max_score
        else:
            min_score = math.inf
            human_symbol = 'X' if ai_symbol == 'O' else 'O'
            for i in range(9):
                if board[i] == '':
                    board[i] = human_symbol
                    score = self.minimax(board, depth + 1, True, ai_symbol)
                    board[i] = ''
                    min_score = min(score, min_score)
            return min_score
    
    def minimax_alpha_beta(self, board, depth, is_maximizing, ai_symbol, alpha, beta):
        """
        Minimax algorithm with Alpha-Beta Pruning and depth limit for speed
        """
        # Check terminal states
        winner = self.check_winner(board)
        if winner == ai_symbol:
            return 10 - depth
        elif winner and winner != ai_symbol:
            return depth - 10
        elif self.is_board_full(board):
            return 0
        
        # Depth limit for faster response (max 6 moves ahead)
        if depth >= 6:
            return 0
        
        if is_maximizing:
            max_score = -math.inf
            for i in range(9):
                if board[i] == '':
                    board[i] = ai_symbol
                    score = self.minimax_alpha_beta(
                        board, depth + 1, False, ai_symbol, alpha, beta
                    )
                    board[i] = ''
                    max_score = max(score, max_score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break  # Alpha-Beta Pruning
            return max_score
        else:
            min_score = math.inf
            human_symbol = 'X' if ai_symbol == 'O' else 'O'
            for i in range(9):
                if board[i] == '':
                    board[i] = human_symbol
                    score = self.minimax_alpha_beta(
                        board, depth + 1, True, ai_symbol, alpha, beta
                    )
                    board[i] = ''
                    min_score = min(score, min_score)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break  # Alpha-Beta Pruning
            return min_score
    
    def check_winner(self, board):
        """
        Check if there's a winner on the board
        """
        for combo in self.winning_combinations:
            if (board[combo[0]] != '' and 
                board[combo[0]] == board[combo[1]] == board[combo[2]]):
                return board[combo[0]]
        return None
    
    def is_board_full(self, board):
        """
        Check if the board is completely filled
        """
        return '' not in board
    
    def get_empty_positions(self, board):
        """
        Get all empty positions on the board
        """
        return [i for i in range(9) if board[i] == '']
