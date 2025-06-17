import React from 'react';
import styled from 'styled-components';

export const Button = styled.button`
  padding: 10px 15px;
  border: none;
  background: #0065eb;
  border-radius: 5px;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #0056d3;
  }

  &:disabled {
    background: #ccc;
    color: #666;
    cursor: not-allowed;
    opacity: 0.6;
  }

  &:disabled:hover {
    background: #ccc;
  }
`;
