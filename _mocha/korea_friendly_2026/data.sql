create table clients(
    id int auto_increment primary key,
    api_key varchar(255) not null,
    created_at timestamp default current_timestamp
);
create table projects(
    id int auto_increment primary key,
    name varchar(255) not null,
    description text,
    client_id int not null references clients(id),
    created_at timestamp default current_timestamp
);
create table data_files(
    id int auto_increment primary key,
    project_id int not null references projects(id),
    filename varchar(255) not null,
    s3_key varchar(512) not null,
    size int not null,
    uploaded_at timestamp default current_timestamp
);
create table processing_jobs(
    id char(36) primary key,
    project_id int not null references projects(id),
    status varchar(50) not null,
    result_path varchar(512),
    started_at timestamp default current_timestamp,
    completed_at timestamp null
);