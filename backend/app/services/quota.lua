-- All keys share a Redis hash tag. Redis time prevents application clock drift.
local now = tonumber(redis.call('TIME')[1])
local minute, peer, active, daily = KEYS[1], KEYS[2], KEYS[3], KEYS[4]
local day = math.floor(now / 86400)
if tonumber(redis.call('HGET', daily, 'day') or '-1') ~= day then
  redis.call('HSET', daily, 'day', day, 'count', 0)
end
redis.call('ZREMRANGEBYSCORE', minute, '-inf', now - 60)
redis.call('ZREMRANGEBYSCORE', peer, '-inf', now - 60)
redis.call('ZREMRANGEBYSCORE', active, '-inf', now - 75)
if tonumber(redis.call('HGET', daily, 'count') or '0') >= tonumber(ARGV[5]) then
  return 'daily'
end
if redis.call('ZCARD', minute) >= tonumber(ARGV[2]) or
   redis.call('ZCARD', peer) >= tonumber(ARGV[3]) or
   redis.call('ZCARD', active) >= tonumber(ARGV[4]) then
  return 'limited'
end
redis.call('ZADD', minute, now, ARGV[1])
redis.call('ZADD', peer, now, ARGV[1])
redis.call('ZADD', active, now, ARGV[1])
redis.call('EXPIRE', minute, 120)
redis.call('EXPIRE', peer, 120)
redis.call('EXPIRE', active, 150)
redis.call('HINCRBY', daily, 'count', 1)
redis.call('EXPIRE', daily, 172800)
return 'ok'
