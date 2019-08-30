if (process.env.NODE_ENV === 'development') {
  require('dotenv').config({ silent: true })
}

const config = {
  db: {
    client: 'sqlite3',
    connection: {
      filename: "./data/tgcnbot.db"
    },
    useNullAsDefault: true,
    migrations: {
      tableName: 'knex_migrations',
      directory: './app/migrations',
    },
    seeds: {
      directory: './app/seeds'
    }
  },
  telegram: {
    token: process.env.TELEGRAM_TOKEN
  }
};
  
module.exports = config;