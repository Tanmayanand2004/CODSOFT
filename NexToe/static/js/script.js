let gameState = {
    board: ['', '', '', '', '', '', '', '', ''],
    playerSymbol: 'X',
    aiSymbol: 'O',
    isPlayerTurn: true,
    gameOver: false
};

let isProcessing = false;
let scores = {
    player: 0,
    ai: 0,
    draws: 0
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('NexToe initializing...');
    loadScores();
    createBoard();
    setupEventListeners();
    showSymbolSelection();
});

function loadScores() {
    const saved = localStorage.getItem('nextoe-scores');
    if (saved) {
        scores = JSON.parse(saved);
    }
    updateScoreDisplay();
}

function saveScores() {
    localStorage.setItem('nextoe-scores', JSON.stringify(scores));
}

function updateScoreDisplay() {
    document.getElementById('player-score').textContent = scores.player;
    document.getElementById('ai-score').textContent = scores.ai;
    document.getElementById('draw-score').textContent = scores.draws;
}

function createBoard() {
    console.log('Creating board...');
    const gameBoard = document.getElementById('game-board');
    gameBoard.innerHTML = '';
    
    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('button');
        cell.className = 'cell';
        cell.dataset.index = i;
        cell.onclick = function() { handleCellClick(this); };
        gameBoard.appendChild(cell);
    }
    console.log('Board created with 9 cells');
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Control buttons
    const resetBtn = document.getElementById('reset-btn');
    const themeBtn = document.getElementById('theme-btn');
    
    if (resetBtn) {
        resetBtn.onclick = function() {
            console.log('Reset button clicked');
            showSymbolSelection();
        };
    } else {
        console.error('Reset button not found');
    }
    
    if (themeBtn) {
        themeBtn.onclick = toggleTheme;
    } else {
        console.error('Theme button not found');
    }
    
    // Load theme
    const savedTheme = localStorage.getItem('nextoe-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton();
    
    console.log('Initial event listeners setup complete');
}

function handleCellClick(cell) {
    console.log('Cell clicked:', cell.dataset.index);
    
    if (isProcessing || gameState.gameOver || !gameState.isPlayerTurn) {
        console.log('Click ignored - processing, game over, or not player turn');
        return;
    }
    
    if (cell.textContent !== '' || cell.disabled) {
        console.log('Click ignored - cell occupied');
        return;
    }
    
    const index = parseInt(cell.dataset.index);
    makePlayerMove(index);
}

async function makePlayerMove(position) {
    console.log(`Making player move at position ${position}`);
    isProcessing = true;
    
    // Show visual feedback immediately but don't update game state yet
    const cell = document.querySelector(`[data-index="${position}"]`);
    cell.textContent = gameState.playerSymbol;
    cell.classList.add('filled');
    
    updateStatusMessage('AI is thinking...');
    
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: gameState.board, // Send current board state (without the move)
                position: position,
                player: gameState.playerSymbol
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Move response:', data);
        
        if (data.error) {
            // Revert visual move on error
            cell.textContent = '';
            cell.classList.remove('filled');
            showErrorMessage(data.error);
            return;
        }
        
        // Update game state from server response
        gameState.board = data.board;
        updateBoard();
        
        if (data.game_over) {
            gameState.gameOver = true;
            handleGameEnd(data.winner, data.winning_line);
        } else {
            gameState.isPlayerTurn = true;
            updateStatusMessage('Your turn!');
        }
        
    } catch (error) {
        console.error('Error making move:', error);
        // Revert visual move
        cell.textContent = '';
        cell.classList.remove('filled');
        showErrorMessage('Connection error. Try again.');
    } finally {
        isProcessing = false;
    }
}

function updateBoard() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        const value = gameState.board[index];
        cell.textContent = value;
        cell.className = value ? 'cell filled' : 'cell';
    });
}

function updateCell(index, symbol) {
    const cell = document.querySelector(`[data-index="${index}"]`);
    if (cell) {
        cell.textContent = symbol;
        cell.classList.add('filled');
        gameState.board[index] = symbol;
    }
}

function clearCell(index) {
    const cell = document.querySelector(`[data-index="${index}"]`);
    if (cell) {
        cell.textContent = '';
        cell.classList.remove('filled');
        gameState.board[index] = '';
    }
}

function showSymbolSelection() {
    const overlay = document.createElement('div');
    overlay.className = 'symbol-selection-overlay';
    overlay.innerHTML = `
        <div class="symbol-selection-modal">
            <h3>Choose Your Symbol</h3>
            <div class="symbol-buttons">
                <button class="symbol-btn" data-symbol="X">
                    <span class="symbol">X</span>
                    <span class="text">Play as X (You go first)</span>
                </button>
                <button class="symbol-btn" data-symbol="O">
                    <span class="symbol">O</span>
                    <span class="text">Play as O (AI goes first)</span>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    overlay.querySelectorAll('.symbol-btn').forEach(btn => {
        btn.onclick = function() {
            const symbol = this.dataset.symbol;
            selectSymbol(symbol);
            overlay.remove();
        };
    });
}

async function selectSymbol(symbol) {
    gameState.playerSymbol = symbol;
    gameState.aiSymbol = symbol === 'X' ? 'O' : 'X';
    gameState.isPlayerTurn = symbol === 'X';
    gameState.gameOver = false;
    gameState.board = ['', '', '', '', '', '', '', '', ''];
    
    updateBoard();
    updateTurnIndicator();
    
    // If player chose O, AI goes first
    if (symbol === 'O') {
        updateStatusMessage('AI is making first move...');
        await makeAIFirstMove();
    } else {
        updateStatusMessage('Your turn!');
    }
}

async function makeAIFirstMove() {
    isProcessing = true;
    
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: gameState.board,
                position: -1, // Signal for AI first move
                player: gameState.playerSymbol
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('AI first move response:', data);
        
        if (data.error) {
            showErrorMessage(data.error);
            return;
        }
        
        gameState.board = data.board;
        updateBoard();
        gameState.isPlayerTurn = true;
        updateStatusMessage('Your turn!');
        updateTurnIndicator();
        
    } catch (error) {
        console.error('Error with AI first move:', error);
        showErrorMessage('Failed to get AI move');
    } finally {
        isProcessing = false;
    }
}

function handleGameEnd(winner, winningLine) {
    gameState.gameOver = true;
    gameState.isPlayerTurn = false;
    
    if (winningLine) {
        highlightWinningLine(winningLine);
    }
    
    updateScores(winner);
    
    setTimeout(() => {
        showResultModal(winner);
    }, 1000);
}

function updateScores(winner) {
    if (winner === gameState.playerSymbol) {
        scores.player++;
    } else if (winner === gameState.aiSymbol) {
        scores.ai++;
    } else {
        scores.draws++;
    }
    
    updateScoreDisplay();
    saveScores();
}

function highlightWinningLine(winningLine) {
    winningLine.forEach(index => {
        const cell = document.querySelector(`[data-index="${index}"]`);
        if (cell) {
            cell.classList.add('winning-cell');
        }
    });
}

function showResultModal(winner) {
    console.log('Showing result modal for winner:', winner);
    const modal = document.getElementById('result-modal');
    const title = document.getElementById('result-title');
    const message = document.getElementById('result-message');
    
    if (winner === 'draw') {
        title.textContent = "It's a Draw!";
        message.textContent = "Good game! Want to play again?";
        title.style.color = 'var(--warning-color)';
    } else if (winner === gameState.playerSymbol) {
        title.textContent = "You Win!";
        message.textContent = "Congratulations! You beat the AI!";
        title.style.color = 'var(--success-color)';
    } else {
        title.textContent = "AI Wins!";
        message.textContent = "Better luck next time!";
        title.style.color = 'var(--danger-color)';
    }
    
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
        // Re-setup modal button listeners after modal is shown
        setupModalListeners();
    }, 10);
}

function setupModalListeners() {
    console.log('Setting up modal listeners...');
    const playAgainBtn = document.getElementById('play-again-btn');
    const closeModalBtn = document.getElementById('close-modal');
    
    if (playAgainBtn) {
        // Remove any existing listeners and add new one
        playAgainBtn.onclick = function() {
            console.log('Play again button clicked!');
            closeModal();
            setTimeout(() => {
                showSymbolSelection();
            }, 300);
        };
        console.log('Play again button listener set up successfully');
    } else {
        console.error('Play again button not found in modal');
    }
    
    if (closeModalBtn) {
        closeModalBtn.onclick = function() {
            console.log('Close modal button clicked');
            closeModal();
        };
    } else {
        console.error('Close modal button not found');
    }
}

function closeModal() {
    console.log('Closing modal...');
    const modal = document.getElementById('result-modal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

async function resetGame() {
    try {
        const response = await fetch('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            gameState.board = data.board;
            gameState.gameOver = false;
            gameState.isPlayerTurn = true;
            updateBoard();
            clearWinningEffects();
            showSymbolSelection();
        }
    } catch (error) {
        console.error('Error resetting game:', error);
        showErrorMessage('Failed to reset game');
    }
}

function clearWinningEffects() {
    document.querySelectorAll('.winning-cell').forEach(cell => {
        cell.classList.remove('winning-cell');
    });
    
    const winningLine = document.querySelector('.winning-line');
    if (winningLine) {
        winningLine.remove();
    }
}

function updateTurnIndicator() {
    const turnText = document.getElementById('turn-text');
    const turnIcon = document.getElementById('turn-icon');
    
    if (!turnText || !turnIcon) return;
    
    if (gameState.gameOver) {
        turnText.textContent = 'Game Over';
        turnIcon.textContent = '🎯';
    } else if (gameState.isPlayerTurn) {
        turnText.textContent = 'Your Turn';
        turnIcon.textContent = gameState.playerSymbol;
    } else {
        turnText.textContent = 'AI Turn';
        turnIcon.textContent = gameState.aiSymbol;
    }
}

function updateStatusMessage(message) {
    const statusElement = document.getElementById('turn-text');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

function showErrorMessage(message) {
    const turnText = document.getElementById('turn-text');
    if (!turnText) return;
    
    const originalText = turnText.textContent;
    turnText.textContent = message;
    turnText.style.color = 'var(--danger-color)';
    
    setTimeout(() => {
        turnText.textContent = originalText;
        turnText.style.color = '';
    }, 3000);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('nextoe-theme', newTheme);
    updateThemeButton();
}

function updateThemeButton() {
    const btn = document.getElementById('theme-btn');
    const icon = btn.querySelector('i');
    const currentTheme = document.documentElement.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        icon.className = 'fas fa-sun';
        btn.title = 'Switch to Light Mode';
    } else {
        icon.className = 'fas fa-moon';
        btn.title = 'Switch to Dark Mode';
    }
}
