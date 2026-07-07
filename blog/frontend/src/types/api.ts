export interface UserPublic {
  id: number;
  username: string;
  image_file: string | null;
  image_path: string;
}

export interface UserPrivate {
  id: number;
  username: string;
  image_file: string | null;
  image_path: string;
  email: string;
}

export interface PostResponse {
  id: number;
  title: string;
  content: string;
  user_id: number;
  date_posted: string;
  author: UserPublic;
}

export interface PaginatedPostsResponse {
  posts: PostResponse[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
