require 'forwardable'

EMPTY = 0
PLAYER = 1
OPPONENT = 2
VALID = 3

DISK_MARK = {
  EMPTY => '-',
  PLAYER => 'o',
  OPPONENT => 'x',
  VALID => '#',
}

class Board
  extend Forwardable
  def_delegators :@cells, :each, :map, :map!

  def initialize
    @cells = Array.new(8) { [0] * 8 }
    @cells[3][4] = PLAYER
    @cells[4][3] = PLAYER
    @cells[3][3] = OPPONENT
    @cells[4][4] = OPPONENT
  end

  def []=(disc_row, disc_col, value)
    @cells[disc_col - 1][disc_row - 1] = value
  end

  def [](disc_row, disc_col)
    return EMPTY if @cells[disc_col - 1].nil? ||  @cells[disc_row - 1].nil?
    @cells[disc_col - 1][disc_row - 1]
  end

  def to_s
    '  ' + (1..8).map {|i| "#{i} " }.join + "\n" +
      @cells.each_with_index.reduce('') do |str, (row, i)|
        "#{str}#{i + 1} #{row.reduce('') {|a, e| a + "#{DISK_MARK[e]} " }}\n"
      end
  end
end


class Othello
  def initialize
    @board = Board.new
    @valid_moves = []
    update_valid_moves
  end

  def update_valid_moves
  end

  def switch_turn
    @board.map! do |row|
      row.map do |cell|
        cell = cell == PLAYER ? OPPONENT : PLAYER if cell != EMPTY
        cell
      end
    end
  end

  def flip(scope, calc_place)
    pos_flip = []
    scope.each do |i|
      # require 'pry'; binding.pry
      place = calc_place.call(i)
      return if @board[*place] == EMPTY
      if @board[*place] == PLAYER
        pos_flip.each {|p| @board[*p] = PLAYER }
        return
      end
      pos_flip << place
    end
  end

  def make_move(move)
    p move
    @board[*move] = PLAYER
    right = 1..(8 - move[0])
    bottom = 1..(8 - move[1])
    left = 1..(move[0])
    top = 1..(move[1])

    directions = {
      right: [
        right, lambda {|i| [move[0] + i, move[1]] }
      ],
      bottom: [
        bottom, lambda {|i| [move[0], move[1] + i] }
      ],
      left: [
        left, lambda {|i| [move[0] - i, move[1]] }
      ],
      top: [
        top, lambda {|i| [move[0], move[1] - i] }
      ],
      top_left: [
        [top, left].min_by {|r| r.size },
        lambda {|i| [move[0] - i, move[1] - i] }
      ],
      bottom_right: [
        [bottom, right].max_by {|r| r.size },
        lambda {|i| [move[0] + i, move[1] + i] }
      ],
      top_right: [
        [top, right].max_by {|r| r.size },
        lambda {|i| [move[0] + i, move[1] - i] }
      ],
      bottom_left: [
        [bottom, left].min_by {|r| r.size },
        lambda {|i| [move[0] - i, move[1] + i] }
      ]
    }
    directions.each_value {|range, calc_place| flip(range, calc_place) }
    switch_turn
  end

  def to_s
    @board.to_s
  end
end



def main
  record = File.readlines('data.csv').map {|l| l.chomp.split(',') }[0]
  othello = Othello.new
  record.each do |r|
    othello.make_move r.split('').map(&:to_i)
    puts othello
  end
  puts othello
end

if __FILE__ == $0
  main
end
