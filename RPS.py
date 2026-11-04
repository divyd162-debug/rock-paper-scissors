def player(prev_play, opponent_history=[], state={}):
    ideal_response = {'P': 'S', 'R': 'P', 'S': 'R'}
    quincy_cycle = ['R', 'R', 'P', 'P', 'S']

    # When prev_play is empty, a new match of 1000 games has started. Reset state.
    if not prev_play:
        opponent_history.clear()
        state.clear()
        state['my_history'] = ['R']
        state['abbey_play_order'] = {
            'RR': 0, 'RP': 0, 'RS': 0,
            'PR': 0, 'PP': 0, 'PS': 0,
            'SR': 0, 'SP': 0, 'SS': 0,
        }
        state['scores'] = {'quincy': 0, 'kris': 0, 'mrugesh': 0, 'abbey': 0}
        state['last_preds'] = {}
        return 'R'

    opponent_history.append(prev_play)

    # Evaluate how accurately each opponent model predicted prev_play
    for bot_name, pred in state.get('last_preds', {}).items():
        if pred == prev_play:
            state['scores'][bot_name] += 1

    # 1. Quincy predictor (repeats cyclic pattern of 5 moves)
    next_quincy = 'R'
    if len(opponent_history) >= 2:
        for i in range(5):
            if [quincy_cycle[i], quincy_cycle[(i + 1) % 5]] == opponent_history[-2:]:
                next_quincy = quincy_cycle[(i + 2) % 5]
                break

    # 2. Kris predictor (counters our last move)
    next_kris = ideal_response[state['my_history'][-1]]

    # 3. Mrugesh predictor (counters our most frequent move in last 10 plays)
    last_ten = state['my_history'][-10:]
    most_freq = max(set(last_ten), key=last_ten.count)
    next_mrugesh = ideal_response[most_freq]

    # 4. Abbey predictor (builds a 2-gram Markov model of our plays)
    prev_my_move = state['my_history'][-1]
    last_two = ''.join(state['my_history'][-2:])
    if len(last_two) == 2:
        state['abbey_play_order'][last_two] = state['abbey_play_order'].get(last_two, 0) + 1
    potentials = [prev_my_move + 'R', prev_my_move + 'P', prev_my_move + 'S']
    sub = {k: state['abbey_play_order'].get(k, 0) for k in potentials}
    abbey_pred = max(sub, key=sub.get)[-1:]
    next_abbey = ideal_response[abbey_pred]

    # Store current predictions to evaluate in the next round
    state['last_preds'] = {
        'quincy': next_quincy,
        'kris': next_kris,
        'mrugesh': next_mrugesh,
        'abbey': next_abbey
    }

    # Initial probe plays to allow bots to establish their distinct behavioral patterns
    probe_moves = ['R', 'P', 'S', 'R', 'P']
    if len(opponent_history) < 20:
        move = probe_moves[len(opponent_history) % len(probe_moves)]
    else:
        # Choose the strategy corresponding to the opponent model with highest prediction score
        best_bot = max(state['scores'], key=state['scores'].get)
        predicted_opp_move = state['last_preds'][best_bot]
        move = ideal_response[predicted_opp_move]

    state['my_history'].append(move)
    return move
