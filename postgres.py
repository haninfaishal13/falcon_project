import psycopg2


"""
create table user_person(
    id_user serial primary key,
    username varchar (255) not null,
    password varchar (255) not null
),
create table hardware(
    id_hardware serial primary key,
    name varchar (255) not null,
    type varchar (255) not null,
    description varchar (255) not null
)
create table node(
    id_node serial primary key,
    name varchar (255) not null, 
    location (255) not null, 
    id_hardware integer not null, 
    id_user integer not null, 
    foreign key (id_hardware) references hardware (id_hardware) on update cascade on delete cascade,
    foreign key (id_user) references user (id_user) on update cascade on delete cascade
)
create table sensor(
    id_sensor serial primary key, 
    name varchar (255) not null, 
    value varchar (255) not null,
    id_hardware integer not null, 
    id_node integer not null, 
    foreign key (id_hardware) references hardware (id_hardware) on update cascade on delete cascade,   
    foreign key (id_node) references node (id_node) on update cascade on delete cascade
) 
create table channel(
    time timestamp, 
    value float not null, 
    id_sensor integer not null, 
    foreign key (id_sensor) references sensor (id_sensor) on update cascade on delete cascade
)
"""

host = "localhost"
database = "postgres"
user = "postgres"
password = "postgres"
port = "5432"

conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
curr = conn.cursor()

curr.execute('''create table user_person(
                    id_user serial primary key,
                    username varchar (255) not null,
                    password varchar (255) not null
                ),
                create table hardware(
                    id_hardware serial primary key,
                    name varchar (255) not null,
                    type varchar (255) not null,
                    description varchar (255) not null
                )
                create table node(
                    id_node serial primary key,
                    name varchar (255) not null, 
                    location (255) not null, 
                    id_hardware integer not null, 
                    id_user integer not null, 
                    foreign key (id_hardware) references hardware (id_hardware) on update cascade on delete cascade,
                    foreign key (id_user) references user (id_user) on update cascade on delete cascade
                )
                create table sensor(
                    id_sensor serial primary key, 
                    name varchar (255) not null, 
                    value varchar (255) not null,
                    id_hardware integer not null, 
                    id_node integer not null, 
                    foreign key (id_hardware) references hardware (id_hardware) on update cascade on delete cascade,   
                    foreign key (id_node) references node (id_node) on update cascade on delete cascade
                ) 
                create table channel(
                    time timestamp, 
                    value float not null, 
                    id_sensor integer not null, 
                    foreign key (id_sensor) references sensor (id_sensor) on update cascade on delete cascade
                )''')
