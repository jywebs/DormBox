import React from 'react'

declare global {
  declare module 'react' {
    interface JSX extends React.JSX {}
  }
}